from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, cast

from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from imednet.models.records import Record

from .chunked_pipeline import DEFAULT_CHUNK_SIZE

if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK

DEFAULT_CACHE_DIR = Path.home() / ".imednet" / "cache"


def get_cache_connection(db_path: str | Path) -> sqlite3.Connection:
    """Return a SQLite connection configured for concurrent cache access."""
    resolved_path = Path(db_path).expanduser()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


class CachedRecordsLoader:
    """Load study records through a local SQLite cache with incremental sync."""

    def __init__(
        self,
        sdk: "ImednetSDK",
        *,
        cache_dir: str | Path | None = None,
        database_name: str = "records_cache.sqlite3",
        retry_attempts: int = 3,
    ) -> None:
        self._sdk = sdk
        base_dir = DEFAULT_CACHE_DIR if cache_dir is None else Path(cache_dir).expanduser()
        self.db_path = base_dir / database_name
        self._retry_attempts = retry_attempts
        self._initialise_cache()

    def load_records(self, study_key: str, *, reconcile: bool = True) -> list[Record]:
        """Synchronise the cache for ``study_key`` and return cached records."""
        conn = get_cache_connection(self.db_path)
        try:
            high_water_mark = self._get_high_water_mark(conn, study_key)
            delta_records = self._fetch_delta_records(study_key, high_water_mark)
            self._upsert_records(conn, delta_records)
            if reconcile:
                active_record_ids = self._fetch_active_record_ids(study_key)
                self.reconcile_cache(conn, study_key, active_record_ids)
            return self.get_cached_records(study_key, conn=conn)
        finally:
            conn.close()

    def get_cached_records(
        self, study_key: str, *, conn: sqlite3.Connection | None = None
    ) -> list[Record]:
        """Return cached records for ``study_key`` without contacting the API."""
        return list(self.iter_cached_records(study_key, conn=conn))

    def iter_cached_records(
        self,
        study_key: str,
        *,
        conn: sqlite3.Connection | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> Iterator[Record]:
        """Yield cached records for ``study_key`` in bounded chunks."""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        close_conn = False
        if conn is None:
            conn = get_cache_connection(self.db_path)
            close_conn = True
        try:
            cursor = conn.execute(
                """
                SELECT payload
                FROM record_cache
                WHERE study_key = ?
                ORDER BY record_id
                """,
                (study_key,),
            )
            while True:
                rows = cursor.fetchmany(chunk_size)
                if not rows:
                    break
                for row in rows:
                    yield Record.from_json(json.loads(cast(str, row["payload"])))
        finally:
            if close_conn:
                conn.close()

    def reconcile_cache(
        self, conn: sqlite3.Connection, study_key: str, active_record_ids: set[int]
    ) -> None:
        """Prune records removed from the upstream EDC backend."""
        local_rows = conn.execute(
            "SELECT record_id FROM record_cache WHERE study_key = ?",
            (study_key,),
        ).fetchall()
        local_ids = {cast(int, row["record_id"]) for row in local_rows}
        orphaned_ids = local_ids - active_record_ids
        if orphaned_ids:
            with conn:
                conn.executemany(
                    "DELETE FROM record_cache WHERE study_key = ? AND record_id = ?",
                    [(study_key, orphaned_id) for orphaned_id in orphaned_ids],
                )

    def _initialise_cache(self) -> None:
        conn = get_cache_connection(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS record_cache (
                    study_key TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    form_key TEXT NOT NULL,
                    date_modified TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (study_key, record_id)
                )
                """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_record_cache_study_modified
                ON record_cache (study_key, date_modified)
                """)
            conn.commit()
        finally:
            conn.close()

    def _get_high_water_mark(self, conn: sqlite3.Connection, study_key: str) -> str | None:
        row = conn.execute(
            "SELECT MAX(date_modified) AS max_date_modified FROM record_cache WHERE study_key = ?",
            (study_key,),
        ).fetchone()
        if row is None:
            return None
        return cast(str | None, row["max_date_modified"])

    def _fetch_delta_records(self, study_key: str, high_water_mark: str | None) -> list[Record]:
        filters: dict[str, Any] = {"study_key": study_key, "record_data_filter": None}
        if high_water_mark:
            filters["date_modified"] = (">", high_water_mark)
        return self._list_records(**filters)

    def _fetch_active_record_ids(self, study_key: str) -> set[int]:
        records = self._list_records(study_key=study_key, record_data_filter=None, deleted=False)
        return {record.record_id for record in records}

    def _list_records(self, **filters: Any) -> list[Record]:
        retryer = Retrying(
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        return cast(list[Record], retryer(self._sdk.records.list, **filters))

    def _upsert_records(self, conn: sqlite3.Connection, records: Iterable[Record]) -> None:
        payloads = [
            (
                record.study_key,
                record.record_id,
                record.form_key,
                record.date_modified.isoformat(),
                json.dumps(record.model_dump(mode="json", by_alias=True), sort_keys=True),
            )
            for record in records
        ]
        if not payloads:
            return

        with conn:
            conn.executemany(
                """
                INSERT INTO record_cache (study_key, record_id, form_key, date_modified, payload)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(study_key, record_id) DO UPDATE SET
                    form_key = excluded.form_key,
                    date_modified = excluded.date_modified,
                    payload = excluded.payload
                """,
                payloads,
            )
