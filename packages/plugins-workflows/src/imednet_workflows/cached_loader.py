"""Cached records loader with SQLite delta sync and reconciliation."""

from __future__ import annotations

import contextlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Optional, Set

from tenacity import Retrying, stop_after_attempt, wait_exponential

from imednet.models.records import Record

if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK

ALWAYS_RECONCILE_INTERVAL_SECONDS = 0
DEFAULT_RECONCILE_INTERVAL_SECONDS = 900


def get_cache_connection(db_path: str) -> sqlite3.Connection:
    """Create a SQLite cache connection configured for concurrent access."""
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn


class CachedRecordsLoader:
    """Incremental records loader backed by a local SQLite cache."""

    def __init__(
        self,
        sdk: "ImednetSDK",
        cache_dir: Optional[str] = None,
        db_name: str = "records_cache.sqlite3",
        retry_attempts: int = 3,
        retry_wait_seconds: float = 1.0,
        reconcile_interval_seconds: int = DEFAULT_RECONCILE_INTERVAL_SECONDS,
    ) -> None:
        self._sdk = sdk
        base_dir = Path(cache_dir).expanduser() if cache_dir else Path.home() / ".imednet" / "cache"
        base_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = base_dir / db_name
        self._reconcile_interval_seconds = max(reconcile_interval_seconds, 0)
        self._retryer = Retrying(
            stop=stop_after_attempt(max(retry_attempts, 1)),
            wait=wait_exponential(multiplier=max(retry_wait_seconds, 0.1)),
            reraise=True,
        )
        self._initialize_database()

    @property
    def db_path(self) -> str:
        return str(self._db_path)

    def load_records(self, study_key: str, *, force_reconcile: bool = False) -> List[Record]:
        """Run synchronization and return all cached records for a study."""
        self.sync(study_key, force_reconcile=force_reconcile)
        return self.get_cached_records(study_key)

    def sync(self, study_key: str, *, force_reconcile: bool = False) -> None:
        """Execute two-stage sync: delta ingestion then hard-delete reconciliation."""
        max_date_modified = self._get_max_date_modified(study_key)
        delta_records = self._fetch_delta_records(study_key, max_date_modified=max_date_modified)
        self._upsert_records(study_key, delta_records)
        self._set_last_delta_modified(
            study_key,
            self._next_max_date_modified(max_date_modified, delta_records),
        )

        if force_reconcile or self._reconciliation_due(study_key):
            active_record_ids = self._fetch_active_record_ids(study_key)
            self.reconcile_cache(study_key, active_record_ids=active_record_ids)
            self._set_last_reconciled(study_key, datetime.now(timezone.utc))

    def get_cached_records(self, study_key: str) -> List[Record]:
        """Return all cached records for a study."""
        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT payload FROM record_cache WHERE study_key = ? ORDER BY record_id",
                (study_key,),
            ).fetchall()
        return [Record.from_json(json.loads(row["payload"])) for row in rows]

    def reconcile_cache(self, study_key: str, active_record_ids: Set[int]) -> None:
        """Hard-prune records deleted from upstream by comparing active record IDs."""
        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            local_rows = conn.execute(
                "SELECT record_id FROM record_cache WHERE study_key = ?",
                (study_key,),
            ).fetchall()
            local_ids = {int(row["record_id"]) for row in local_rows}
            orphaned_ids = local_ids - active_record_ids
            if not orphaned_ids:
                return
            with conn:
                conn.executemany(
                    "DELETE FROM record_cache WHERE study_key = ? AND record_id = ?",
                    [(study_key, orphan_id) for orphan_id in orphaned_ids],
                )

    def _initialize_database(self) -> None:
        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS record_cache (
                        study_key TEXT NOT NULL,
                        record_id INTEGER NOT NULL,
                        date_modified TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        PRIMARY KEY (study_key, record_id)
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cache_metadata (
                        study_key TEXT PRIMARY KEY,
                        last_reconciled_at TEXT,
                        last_delta_modified TEXT
                    )
                    """
                )
                columns = {
                    row["name"]
                    for row in conn.execute("PRAGMA table_info(cache_metadata)").fetchall()
                }
                if "last_delta_modified" not in columns:
                    conn.execute("ALTER TABLE cache_metadata ADD COLUMN last_delta_modified TEXT")

    def _get_max_date_modified(self, study_key: str) -> Optional[str]:
        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            metadata_row = conn.execute(
                "SELECT last_delta_modified FROM cache_metadata WHERE study_key = ?",
                (study_key,),
            ).fetchone()
            if metadata_row and metadata_row["last_delta_modified"]:
                return metadata_row["last_delta_modified"]

            row = conn.execute(
                (
                    "SELECT MAX(date_modified) AS max_date_modified "
                    "FROM record_cache WHERE study_key = ?"
                ),
                (study_key,),
            ).fetchone()
        if not row:
            return None
        return row["max_date_modified"]

    def _fetch_delta_records(
        self, study_key: str, *, max_date_modified: Optional[str]
    ) -> List[Record]:
        filters = {}
        if max_date_modified:
            filters["date_modified"] = (">", max_date_modified)

        def _request() -> List[Record]:
            return self._sdk.records.list(
                study_key=study_key,
                record_data_filter=None,
                **filters,
            )

        return self._retryer(_request)

    def _fetch_active_record_ids(self, study_key: str) -> Set[int]:
        def _request() -> Set[int]:
            records = self._sdk.records.list(
                study_key=study_key,
                record_data_filter=None,
                deleted=False,
            )
            return {int(record.record_id) for record in records}

        return self._retryer(_request)

    def _upsert_records(self, study_key: str, records: Iterable[Record]) -> None:
        payloads = []
        for record in records:
            record_data = record.model_dump(mode="json", by_alias=True)
            payloads.append(
                (
                    study_key,
                    int(record.record_id),
                    self._normalize_datetime(record.date_modified),
                    json.dumps(record_data, default=str),
                )
            )

        if not payloads:
            return

        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            with conn:
                conn.executemany(
                    """
                    INSERT INTO record_cache(study_key, record_id, date_modified, payload)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(study_key, record_id)
                    DO UPDATE SET
                        date_modified = excluded.date_modified,
                        payload = excluded.payload
                    """,
                    payloads,
                )

    def _reconciliation_due(self, study_key: str) -> bool:
        if self._reconcile_interval_seconds == ALWAYS_RECONCILE_INTERVAL_SECONDS:
            return True
        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            row = conn.execute(
                "SELECT last_reconciled_at FROM cache_metadata WHERE study_key = ?",
                (study_key,),
            ).fetchone()

        if not row or not row["last_reconciled_at"]:
            return True

        last_reconciled = datetime.fromisoformat(row["last_reconciled_at"])
        if last_reconciled.tzinfo is None:
            last_reconciled = last_reconciled.replace(tzinfo=timezone.utc)
        elapsed_seconds = (datetime.now(timezone.utc) - last_reconciled).total_seconds()
        return elapsed_seconds >= self._reconcile_interval_seconds

    def _set_last_reconciled(self, study_key: str, value: datetime) -> None:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO cache_metadata(study_key, last_reconciled_at)
                    VALUES (?, ?)
                    ON CONFLICT(study_key)
                    DO UPDATE SET last_reconciled_at = excluded.last_reconciled_at
                    """,
                    (study_key, value.isoformat()),
                )

    def _set_last_delta_modified(self, study_key: str, value: Optional[str]) -> None:
        if not value:
            return
        with contextlib.closing(get_cache_connection(self.db_path)) as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO cache_metadata(study_key, last_delta_modified)
                    VALUES (?, ?)
                    ON CONFLICT(study_key)
                    DO UPDATE SET last_delta_modified = excluded.last_delta_modified
                    """,
                    (study_key, value),
                )

    def _next_max_date_modified(
        self, previous_max: Optional[str], records: Iterable[Record]
    ) -> Optional[str]:
        current_max = previous_max
        for record in records:
            candidate = self._normalize_datetime(record.date_modified)
            if current_max is None or candidate > current_max:
                current_max = candidate
        return current_max

    @staticmethod
    def _normalize_datetime(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
