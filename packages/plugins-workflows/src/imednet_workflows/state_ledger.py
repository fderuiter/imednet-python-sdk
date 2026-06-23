"""Stateful incremental high-water mark tracker for workflow streams."""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from pydantic import BaseModel, Field

# Graceful fallback if fcntl is not available (e.g. non-UNIX environments)
try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore[assignment]


class StreamState(BaseModel):
    """Schema for individual stream execution checkpoints."""

    last_timestamp: datetime
    records_processed: int = 0
    last_run_status: str = "success"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StudyState(BaseModel):
    """Schema for all streams in a given study context."""

    streams: Dict[str, StreamState] = Field(default_factory=dict)


class LedgerState(BaseModel):
    """Schema for the entire ledger file containing all studies."""

    studies: Dict[str, StudyState] = Field(default_factory=dict)


class ExtractionStateLedger:
    """Manages transactional state bookmarks per study to guarantee absolute ingestion tracking."""

    def __init__(self, ledger_path: str = "/var/lib/imednet/pipeline_ledger.json") -> None:
        """Initialize the extraction state ledger.

        Args:
            ledger_path: Path to the JSON file where state is persisted.
        """
        self.ledger_path = Path(ledger_path)
        self._lock_path = self.ledger_path.with_suffix(".lock")

    def _ensure_ledger_exists(self) -> None:
        """Ensure the ledger file and its parent directory exist."""
        if not self.ledger_path.exists():
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump({"studies": {}}, f, indent=2)

    @contextlib.contextmanager
    def _lock(self) -> Generator[None, None, None]:
        """Cross-process file lock using flock on UNIX."""
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        if fcntl is None:
            # Fallback for systems without fcntl (e.g. Windows)
            yield
            return

        with open(self._lock_path, "w") as lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)  # type: ignore[attr-defined]
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)  # type: ignore[attr-defined]

    def read_state(self) -> LedgerState:
        """Reads and validates the current ledger state."""
        self._ensure_ledger_exists()
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # If file is empty or corrupted, fallback to empty ledger
                return LedgerState(studies={})
        return LedgerState.model_validate(data)

    def write_state(self, state: LedgerState) -> None:
        """Writes the ledger state atomically using a temporary file."""
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        # Serialize first to ensure the data is perfectly valid
        serialized = state.model_dump_json(indent=2)

        dir_name = self.ledger_path.parent
        # Write to temp file in the same directory, then rename atomically
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
            tf.write(serialized)
            temp_name = tf.name

        try:
            os.replace(temp_name, self.ledger_path)
        except Exception:
            # Cleanup temp file on failure
            if os.path.exists(temp_name):
                os.remove(temp_name)
            raise

    def get_last_timestamp(self, study_key: str, stream_name: str) -> Optional[datetime]:
        """Returns the high-water mark timestamp for a given study and stream."""
        with self._lock():
            state = self.read_state()
            study = state.studies.get(study_key)
            if not study:
                return None
            stream = study.streams.get(stream_name)
            if not stream:
                return None
            # Ensure return datetime is timezone-aware
            ts = stream.last_timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return ts

    def set_last_timestamp(
        self,
        study_key: str,
        stream_name: str,
        timestamp: datetime,
        records_processed: int = 0,
        status: str = "success",
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Sets the high-water mark timestamp atomically."""
        with self._lock():
            state = self.read_state()
            study = state.studies.setdefault(study_key, StudyState())

            # Ensure timezone-aware datetime
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            study.streams[stream_name] = StreamState(
                last_timestamp=timestamp,
                records_processed=records_processed,
                last_run_status=status,
                error_message=error_message,
                metadata=metadata or {},
            )
            self.write_state(state)

    @contextlib.contextmanager
    def transaction(
        self,
        study_key: str,
        stream_name: str,
        fallback_timestamp: Optional[datetime] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for transactional state tracking.

        Yields a dict where user can record 'records_processed', 'new_timestamp', and 'metadata'.
        Saves automatically upon exiting the context with no exceptions.
        The ledger file lock is held for the entire duration of the context.
        """
        with self._lock():
            state = self.read_state()
            study = state.studies.get(study_key)
            last_ts: Optional[datetime] = None
            if study:
                stream_state = study.streams.get(stream_name)
                if stream_state:
                    last_ts = stream_state.last_timestamp
                    if last_ts.tzinfo is None:
                        last_ts = last_ts.replace(tzinfo=timezone.utc)
            if last_ts is None:
                last_ts = fallback_timestamp
            if last_ts is not None and last_ts.tzinfo is None:
                last_ts = last_ts.replace(tzinfo=timezone.utc)

            tx_data: Dict[str, Any] = {
                "last_timestamp": last_ts,
                "new_timestamp": None,
                "records_processed": 0,
                "metadata": {},
            }
            try:
                yield tx_data
                # Commit changes only if successful and new_timestamp is set
                new_ts = tx_data.get("new_timestamp")
                if new_ts:
                    if new_ts.tzinfo is None:
                        new_ts = new_ts.replace(tzinfo=timezone.utc)
                    study_entry = state.studies.setdefault(study_key, StudyState())
                    study_entry.streams[stream_name] = StreamState(
                        last_timestamp=new_ts,
                        records_processed=tx_data.get("records_processed", 0),
                        last_run_status="success",
                        metadata=tx_data.get("metadata") or {},
                    )
                    self.write_state(state)
            except Exception as err:
                # Mark stream as failed
                err_ts = tx_data.get("new_timestamp") or last_ts or datetime.now(timezone.utc)
                if err_ts.tzinfo is None:
                    err_ts = err_ts.replace(tzinfo=timezone.utc)
                study_entry = state.studies.setdefault(study_key, StudyState())
                study_entry.streams[stream_name] = StreamState(
                    last_timestamp=err_ts,
                    records_processed=tx_data.get("records_processed", 0),
                    last_run_status="failed",
                    error_message=str(err),
                    metadata=tx_data.get("metadata") or {},
                )
                self.write_state(state)
                raise

    def delete_entry(self, study_key: str, stream_name: Optional[str] = None) -> bool:
        """Deletes a study or specific stream entry from the ledger under the file lock.

        Returns ``True`` if the entry existed and was removed, ``False`` otherwise.
        """
        with self._lock():
            state = self.read_state()
            if study_key not in state.studies:
                return False
            if stream_name is None:
                del state.studies[study_key]
            else:
                if stream_name not in state.studies[study_key].streams:
                    return False
                del state.studies[study_key].streams[stream_name]
            self.write_state(state)
        return True
