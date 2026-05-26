from __future__ import annotations

import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Callable, Iterator, Optional

from imednet.models.triage import TriageAnnotation, TriageHistoryEntry, TriageItem, TriageStatus

_SAFE_SQL_IDENTIFIER = re.compile(r"^[A-Za-z0-9._:-]+$")


class TriageStore:
    """Thread-safe SQLite-backed triage queue and decision store."""

    def __init__(
        self,
        db_path: str | Path,
        *,
        timeout: float = 30.0,
        retry_attempts: int = 3,
    ) -> None:
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._timeout = timeout
        self._retry_attempts = retry_attempts
        self._lock = RLock()
        self._initialize_schema()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=self._timeout)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_schema(self) -> None:
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS triage_items (
                    item_id TEXT PRIMARY KEY,
                    study_key TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assignee TEXT,
                    severity TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS triage_annotations (
                    annotation_id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(item_id) REFERENCES triage_items(item_id) ON DELETE CASCADE
                )
                """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS triage_history (
                    transition_id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    from_status TEXT NOT NULL,
                    to_status TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    comment TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(item_id) REFERENCES triage_items(item_id) ON DELETE CASCADE
                )
                """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_triage_items_study_status
                ON triage_items(study_key, status)
                """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_triage_annotations_item
                ON triage_annotations(item_id, timestamp)
                """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_triage_history_item
                ON triage_history(item_id, timestamp)
                """)
            conn.commit()

    def get_journal_mode(self) -> str:
        with self._connection() as conn:
            value = conn.execute("PRAGMA journal_mode").fetchone()[0]
        return str(value)

    def _execute_write(self, callback: Callable[[sqlite3.Connection], None]) -> None:
        last_error: sqlite3.OperationalError | None = None
        for _ in range(self._retry_attempts):
            try:
                with self._lock:
                    with self._connection() as conn:
                        with conn:
                            callback(conn)
                return
            except sqlite3.OperationalError as exc:
                last_error = exc
        if last_error is not None:
            raise last_error

    def upsert_item(self, item: TriageItem) -> None:
        now = datetime.now(timezone.utc).isoformat()

        def _write(conn: sqlite3.Connection) -> None:
            conn.execute(
                """
                INSERT INTO triage_items (
                    item_id, study_key, status, assignee, severity, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    study_key=excluded.study_key,
                    status=excluded.status,
                    assignee=excluded.assignee,
                    severity=excluded.severity,
                    updated_at=excluded.updated_at
                """,
                (
                    item.item_id,
                    item.study_key,
                    item.status.value,
                    item.assignee,
                    item.severity,
                    now,
                    now,
                ),
            )

            conn.execute("DELETE FROM triage_annotations WHERE item_id = ?", (item.item_id,))
            conn.executemany(
                """
                INSERT INTO triage_annotations (annotation_id, item_id, user_id, comment, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        annotation.annotation_id,
                        item.item_id,
                        annotation.user_id,
                        annotation.comment,
                        annotation.timestamp.isoformat(),
                    )
                    for annotation in item.annotations
                ],
            )

            conn.execute("DELETE FROM triage_history WHERE item_id = ?", (item.item_id,))
            conn.executemany(
                """
                INSERT INTO triage_history (
                    transition_id, item_id, from_status, to_status, user_id, comment, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        entry.transition_id,
                        item.item_id,
                        entry.from_status.value,
                        entry.to_status.value,
                        entry.user_id,
                        entry.comment,
                        entry.timestamp.isoformat(),
                    )
                    for entry in item.history
                ],
            )

        self._execute_write(_write)

    def get_triage_item(self, item_id: str) -> Optional[TriageItem]:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT item_id, study_key, status, assignee, severity
                FROM triage_items
                WHERE item_id = ?
                """,
                (item_id,),
            ).fetchone()
            if row is None:
                return None

            annotations = self._get_annotations(conn, item_id)
            history = self._get_history(conn, item_id)
            return TriageItem(
                item_id=str(row["item_id"]),
                study_key=str(row["study_key"]),
                status=TriageStatus(str(row["status"])),
                assignee=str(row["assignee"]).strip() if row["assignee"] else None,
                severity=str(row["severity"]),
                annotations=annotations,
                history=history,
            )

    def get_queue(self, study_key: str, status: Optional[TriageStatus] = None) -> list[TriageItem]:
        with self._connection() as conn:
            if status is None:
                rows = conn.execute(
                    """
                    SELECT item_id, study_key, status, assignee, severity
                    FROM triage_items
                    WHERE study_key = ?
                    ORDER BY updated_at ASC
                    """,
                    (study_key,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT item_id, study_key, status, assignee, severity
                    FROM triage_items
                    WHERE study_key = ? AND status = ?
                    ORDER BY updated_at ASC
                    """,
                    (study_key, status.value),
                ).fetchall()

            item_ids = [str(row["item_id"]) for row in rows]
            if not item_ids:
                return []
            invalid_item_id = next(
                (item_id for item_id in item_ids if not _SAFE_SQL_IDENTIFIER.fullmatch(item_id)),
                None,
            )
            if invalid_item_id is not None:
                raise ValueError(
                    f"Invalid triage item identifier: {invalid_item_id}. "
                    "Only alphanumeric characters and ._:- are allowed."
                )

            conn.execute("DROP TABLE IF EXISTS temp_item_ids")
            conn.execute("CREATE TEMP TABLE temp_item_ids (item_id TEXT PRIMARY KEY)")
            conn.executemany(
                "INSERT INTO temp_item_ids (item_id) VALUES (?)",
                [(item_id,) for item_id in item_ids],
            )

            annotation_rows = conn.execute(
                """
                SELECT item_id, annotation_id, user_id, comment, timestamp
                FROM triage_annotations
                WHERE item_id IN (SELECT item_id FROM temp_item_ids)
                ORDER BY timestamp ASC
                """,
            ).fetchall()
            history_rows = conn.execute(
                """
                SELECT item_id, transition_id, from_status, to_status, user_id, comment, timestamp
                FROM triage_history
                WHERE item_id IN (SELECT item_id FROM temp_item_ids)
                ORDER BY timestamp ASC
                """,
            ).fetchall()

            annotations_by_item: dict[str, list[TriageAnnotation]] = {
                item_id: [] for item_id in item_ids
            }
            for annotation_row in annotation_rows:
                item_id = str(annotation_row["item_id"])
                annotations_by_item[item_id].append(
                    TriageAnnotation(
                        annotation_id=str(annotation_row["annotation_id"]),
                        user_id=str(annotation_row["user_id"]),
                        comment=str(annotation_row["comment"]),
                        timestamp=datetime.fromisoformat(str(annotation_row["timestamp"])),
                    )
                )

            history_by_item: dict[str, list[TriageHistoryEntry]] = {
                item_id: [] for item_id in item_ids
            }
            for history_row in history_rows:
                item_id = str(history_row["item_id"])
                history_by_item[item_id].append(
                    TriageHistoryEntry(
                        transition_id=str(history_row["transition_id"]),
                        from_status=TriageStatus(str(history_row["from_status"])),
                        to_status=TriageStatus(str(history_row["to_status"])),
                        user_id=str(history_row["user_id"]),
                        comment=(
                            str(history_row["comment"]).strip() if history_row["comment"] else None
                        ),
                        timestamp=datetime.fromisoformat(str(history_row["timestamp"])),
                    )
                )

            return [
                TriageItem(
                    item_id=str(row["item_id"]),
                    study_key=str(row["study_key"]),
                    status=TriageStatus(str(row["status"])),
                    assignee=str(row["assignee"]).strip() if row["assignee"] else None,
                    severity=str(row["severity"]),
                    annotations=annotations_by_item.get(str(row["item_id"]), []),
                    history=history_by_item.get(str(row["item_id"]), []),
                )
                for row in rows
            ]

    def assign_item(self, item_id: str, assignee: str) -> None:
        def _write(conn: sqlite3.Connection) -> None:
            cursor = conn.execute(
                """
                UPDATE triage_items
                SET assignee = ?, updated_at = ?
                WHERE item_id = ?
                """,
                (assignee.strip(), datetime.now(timezone.utc).isoformat(), item_id),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Unknown triage item: {item_id}")

        self._execute_write(_write)

    def update_status(
        self,
        item_id: str,
        to_status: TriageStatus,
        user_id: str,
        comment: Optional[str],
    ) -> None:
        normalized_comment = comment.strip() if comment else None
        timestamp = datetime.now(timezone.utc).isoformat()

        def _write(conn: sqlite3.Connection) -> None:
            row = conn.execute(
                "SELECT status FROM triage_items WHERE item_id = ?",
                (item_id,),
            ).fetchone()
            if row is None:
                raise ValueError(f"Unknown triage item: {item_id}")

            from_status = TriageStatus(str(row["status"]))
            conn.execute(
                """
                UPDATE triage_items
                SET status = ?, updated_at = ?
                WHERE item_id = ?
                """,
                (to_status.value, timestamp, item_id),
            )
            conn.execute(
                """
                INSERT INTO triage_history (
                    transition_id, item_id, from_status, to_status, user_id, comment, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    item_id,
                    from_status.value,
                    to_status.value,
                    user_id,
                    normalized_comment,
                    timestamp,
                ),
            )

        self._execute_write(_write)

    def add_annotation(self, item_id: str, user_id: str, comment: str) -> None:
        cleaned_comment = comment.strip()
        if not cleaned_comment:
            raise ValueError("Annotation comment must not be empty")

        timestamp = datetime.now(timezone.utc).isoformat()

        def _write(conn: sqlite3.Connection) -> None:
            row = conn.execute(
                "SELECT item_id FROM triage_items WHERE item_id = ?",
                (item_id,),
            ).fetchone()
            if row is None:
                raise ValueError(f"Unknown triage item: {item_id}")

            conn.execute(
                """
                INSERT INTO triage_annotations (annotation_id, item_id, user_id, comment, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(uuid.uuid4()), item_id, user_id, cleaned_comment, timestamp),
            )
            conn.execute(
                "UPDATE triage_items SET updated_at = ? WHERE item_id = ?",
                (timestamp, item_id),
            )

        self._execute_write(_write)

    def get_item_last_updated(self, item_id: str) -> Optional[datetime]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT updated_at FROM triage_items WHERE item_id = ?",
                (item_id,),
            ).fetchone()
        if row is None or row["updated_at"] is None:
            return None
        return datetime.fromisoformat(str(row["updated_at"]))

    def _get_annotations(self, conn: sqlite3.Connection, item_id: str) -> list[TriageAnnotation]:
        rows = conn.execute(
            """
            SELECT annotation_id, user_id, comment, timestamp
            FROM triage_annotations
            WHERE item_id = ?
            ORDER BY timestamp ASC
            """,
            (item_id,),
        ).fetchall()
        return [
            TriageAnnotation(
                annotation_id=str(row["annotation_id"]),
                user_id=str(row["user_id"]),
                comment=str(row["comment"]),
                timestamp=datetime.fromisoformat(str(row["timestamp"])),
            )
            for row in rows
        ]

    def _get_history(self, conn: sqlite3.Connection, item_id: str) -> list[TriageHistoryEntry]:
        rows = conn.execute(
            """
            SELECT transition_id, from_status, to_status, user_id, comment, timestamp
            FROM triage_history
            WHERE item_id = ?
            ORDER BY timestamp ASC
            """,
            (item_id,),
        ).fetchall()
        return [
            TriageHistoryEntry(
                transition_id=str(row["transition_id"]),
                from_status=TriageStatus(str(row["from_status"])),
                to_status=TriageStatus(str(row["to_status"])),
                user_id=str(row["user_id"]),
                comment=str(row["comment"]).strip() if row["comment"] else None,
                timestamp=datetime.fromisoformat(str(row["timestamp"])),
            )
            for row in rows
        ]
