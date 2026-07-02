"""Stateful incremental high-water mark tracker for workflow streams."""

from __future__ import annotations

import abc
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


class BaseStateProvider(abc.ABC):
    """Abstract interface for managing high-water marks and state transactions."""

    @abc.abstractmethod
    def get_last_timestamp(self, study_key: str, stream_name: str) -> Optional[datetime]:
        """Returns the high-water mark timestamp for a given study and stream."""
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    @contextlib.contextmanager
    def transaction(
        self,
        study_key: str,
        stream_name: str,
        fallback_timestamp: Optional[datetime] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for transactional state tracking."""
        pass

    @abc.abstractmethod
    def delete_entry(self, study_key: str, stream_name: Optional[str] = None) -> bool:
        """Deletes a study or specific stream entry from the state.

        Returns ``True`` if the entry existed and was removed, ``False`` otherwise.
        """
        pass

    @abc.abstractmethod
    def read_state(self) -> LedgerState:
        """Reads and validates the current full state (for CLI display)."""
        pass


class FileStateProvider(BaseStateProvider):
    """Manages transactional state bookmarks per study using a local JSON file."""

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


# Backward compatibility alias
ExtractionStateLedger = FileStateProvider


class AirflowStateProvider(BaseStateProvider):
    """Manages transactional state using Airflow XCom metadata."""

    def _get_xcom_key(self, study_key: str, stream_name: str) -> str:
        return f"state_{study_key}_{stream_name}"

    def get_last_timestamp(self, study_key: str, stream_name: str) -> Optional[datetime]:
        """Returns the high-water mark timestamp from Airflow XCom."""
        try:
            from airflow.operators.python import get_current_context

            context = get_current_context()
            ti = context["ti"]
            # Pull from prior dates to get the last successful high-water mark across runs
            val = ti.xcom_pull(
                key=self._get_xcom_key(study_key, stream_name), include_prior_dates=True
            )
            if val and isinstance(val, dict) and "last_timestamp" in val:
                return datetime.fromisoformat(val["last_timestamp"])
        except Exception:
            pass

        # Fallback to DB query if not running within a context
        try:
            from airflow.models.xcom import XCom
            from airflow.utils.session import provide_session

            @provide_session
            def _get_xcom(session=None):
                # Query the latest XCom for this key
                return (
                    session.query(XCom)
                    .filter(XCom.key == self._get_xcom_key(study_key, stream_name))
                    .order_by(XCom.timestamp.desc())
                    .first()
                )

            xcom_obj = _get_xcom()
            if xcom_obj and isinstance(xcom_obj.value, dict) and "last_timestamp" in xcom_obj.value:
                return datetime.fromisoformat(xcom_obj.value["last_timestamp"])
        except ImportError:
            pass
        return None

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
        """Sets the high-water mark timestamp atomically using Airflow XCom."""
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        val = {
            "last_timestamp": timestamp.isoformat(),
            "records_processed": records_processed,
            "status": status,
            "error_message": error_message,
            "metadata": metadata or {},
        }

        try:
            from airflow.operators.python import get_current_context

            context = get_current_context()
            ti = context["ti"]
            ti.xcom_push(key=self._get_xcom_key(study_key, stream_name), value=val)
            return
        except Exception:
            pass

        # Fallback to DB if out of context but within Airflow environment
        try:
            from airflow.models.xcom import XCom

            dag_id = os.environ.get("AIRFLOW_CTX_DAG_ID", "manual_state_sync")
            task_id = os.environ.get("AIRFLOW_CTX_TASK_ID", "manual_state_sync")
            exec_date_str = os.environ.get("AIRFLOW_CTX_EXECUTION_DATE")

            if exec_date_str:
                exec_date = datetime.fromisoformat(exec_date_str)
            else:
                exec_date = datetime.now(timezone.utc)

            XCom.set(
                key=self._get_xcom_key(study_key, stream_name),
                value=val,
                task_id=task_id,
                dag_id=dag_id,
                execution_date=exec_date,
            )
        except ImportError:
            pass

    @contextlib.contextmanager
    def transaction(
        self,
        study_key: str,
        stream_name: str,
        fallback_timestamp: Optional[datetime] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager for transactional state tracking using Airflow XCom."""
        last_ts = self.get_last_timestamp(study_key, stream_name)
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
            new_ts = tx_data.get("new_timestamp")
            if new_ts:
                self.set_last_timestamp(
                    study_key=study_key,
                    stream_name=stream_name,
                    timestamp=new_ts,
                    records_processed=tx_data.get("records_processed", 0),
                    status="success",
                    metadata=tx_data.get("metadata"),
                )
        except Exception as err:
            err_ts = tx_data.get("new_timestamp") or last_ts or datetime.now(timezone.utc)
            self.set_last_timestamp(
                study_key=study_key,
                stream_name=stream_name,
                timestamp=err_ts,
                records_processed=tx_data.get("records_processed", 0),
                status="failed",
                error_message=str(err),
                metadata=tx_data.get("metadata"),
            )
            raise

    def delete_entry(self, study_key: str, stream_name: Optional[str] = None) -> bool:
        """Deletes a study or specific stream entry from XCom."""
        try:
            from airflow.models.xcom import XCom
            from airflow.utils.session import provide_session

            @provide_session
            def _delete_xcom(session=None):
                query = session.query(XCom)
                if stream_name:
                    query = query.filter(XCom.key == self._get_xcom_key(study_key, stream_name))
                else:
                    query = query.filter(XCom.key.like(f"state_{study_key}_%"))

                deleted = query.delete(synchronize_session=False)
                return deleted > 0

            return _delete_xcom()
        except ImportError:
            return False

    def read_state(self) -> LedgerState:
        """Reads and validates the current full state from XComs for CLI display."""
        state = LedgerState()
        try:
            from airflow.models.xcom import XCom
            from airflow.utils.session import provide_session

            @provide_session
            def _get_all_xcoms(session=None):
                return (
                    session.query(XCom)
                    .filter(XCom.key.like("state_%"))
                    .order_by(XCom.timestamp.desc())
                    .all()
                )

            xcoms = _get_all_xcoms()

            # To avoid duplicates if there are multiple XComs for the same key over time,
            # keep track of keys processed. Since it's ordered by desc, first one is latest.
            processed_keys = set()
            for x in xcoms:
                if x.key in processed_keys:
                    continue
                processed_keys.add(x.key)

                parts = x.key.split("_", 2)
                if len(parts) == 3 and parts[0] == "state":
                    s_key = parts[1]
                    s_name = parts[2]

                    val = x.value
                    if isinstance(val, dict) and "last_timestamp" in val:
                        ts = datetime.fromisoformat(val["last_timestamp"])
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)

                        study = state.studies.setdefault(s_key, StudyState())
                        study.streams[s_name] = StreamState(
                            last_timestamp=ts,
                            records_processed=val.get("records_processed", 0),
                            last_run_status=val.get("status", "success"),
                            error_message=val.get("error_message"),
                            metadata=val.get("metadata", {}),
                        )
        except ImportError:
            pass
        return state


def get_state_provider(
    ledger_path: str = "/var/lib/imednet/pipeline_ledger.json",
) -> BaseStateProvider:
    """Factory to get the appropriate state provider based on environment."""
    if "AIRFLOW_CTX_TASK_ID" in os.environ or os.environ.get("USE_AIRFLOW_STATE_PROVIDER") == "1":
        return AirflowStateProvider()
    return FileStateProvider(ledger_path)
