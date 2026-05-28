"""SQLite-backed version control ledger for study configurations.

Provides immutable, append-only commit history with SHA-256 content hashing,
diff capability, and safe rollback.  History blocks are read-only once written.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any

from imednet.spi.models import StudyConfiguration

import os

_DEFAULT_DB_PATH = Path(os.environ.get("IMEDNET_CONFIG_DB_PATH", Path.home() / ".imednet" / "config_versions.sqlite3"))


def _sha256_of(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class ConfigVersionStore:
    """Immutable append-only store for ``StudyConfiguration`` versions.

    Each call to :meth:`commit_config` creates a new entry signed with a
    SHA-256 digest of the serialised configuration body.  History is strictly
    read-only — individual commit rows may never be edited or deleted.

    Args:
        db_path: Filesystem path for the SQLite database.  Defaults to
            ``~/.imednet/config_versions.sqlite3``.
    """

    def __init__(self, db_path: str | Path = _DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize_schema()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_schema(self) -> None:
        with self._lock, self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config_commits (
                    commit_id   TEXT PRIMARY KEY,
                    study_key   TEXT NOT NULL,
                    version_tag TEXT NOT NULL,
                    config_data TEXT NOT NULL,
                    modified_by TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp   TEXT NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_config_commits_study"
                " ON config_commits (study_key, timestamp)"
            )
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_config_commits_no_update
                BEFORE UPDATE ON config_commits
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'Configuration history is immutable and cannot be modified'
                    );
                END;
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_config_commits_no_delete
                BEFORE DELETE ON config_commits
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'Configuration history is immutable and cannot be deleted'
                    );
                END;
            """)
            conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def commit_config(
        self,
        study_key: str,
        config: StudyConfiguration,
        user: str,
        desc: str,
    ) -> str:
        """Serialise *config*, compute its SHA-256 hash, and persist the commit.

        Args:
            study_key: Identifies the study this configuration belongs to.
            config: The :class:`~imednet.models.study_config.StudyConfiguration`
                to store.
            user: Identifier of the person or process making the change.
            desc: Human-readable description of what changed.

        Returns:
            The ``commit_id`` (SHA-256 hex digest of the serialised JSON body).

        Raises:
            ValueError: If a commit with the same content hash already exists
                for this study, indicating a no-op duplicate.
        """
        config_json = json.dumps(config.model_dump(mode="json", by_alias=True), sort_keys=True)
        commit_id = _sha256_of(config_json)
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._lock, self._connection() as conn:
            existing = conn.execute(
                "SELECT 1 FROM config_commits WHERE commit_id = ?", (commit_id,)
            ).fetchone()
            if existing:
                raise ValueError(
                    f"Commit {commit_id!r} already exists — configuration is unchanged."
                )
            conn.execute(
                """
                INSERT INTO config_commits
                    (commit_id, study_key, version_tag, config_data,
                     modified_by, description, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    commit_id,
                    study_key,
                    config.version,
                    config_json,
                    user,
                    desc,
                    timestamp,
                ),
            )
            conn.commit()

        return commit_id

    def get_history(self, study_key: str) -> list[dict[str, Any]]:
        """Return all commits for *study_key*, ordered oldest-first.

        Args:
            study_key: The study whose history should be retrieved.

        Returns:
            A list of dicts, each with keys ``commit_id``, ``study_key``,
            ``version_tag``, ``modified_by``, ``description``, and
            ``timestamp``.  The ``config_data`` body is intentionally omitted
            to keep the payload small — use :meth:`rollback_config` to
            retrieve the full body for a specific commit.
        """
        with self._lock, self._connection() as conn:
            rows = conn.execute(
                """
                SELECT commit_id, study_key, version_tag, config_data,
                       modified_by, description, timestamp
                FROM   config_commits
                WHERE  study_key = ?
                ORDER  BY timestamp ASC
                """,
                (study_key,),
            ).fetchall()
        history: list[dict[str, Any]] = []
        for row in rows:
            commit = dict(row)
            self._verify_commit_signature(commit["commit_id"], commit["config_data"])
            commit.pop("config_data")
            history.append(commit)
        return history

    def diff_configs(self, commit_a: str, commit_b: str) -> dict[str, Any]:
        """Compute a property-level diff between two commits.

        Compares the flat JSON key space of the two commits.  Returns a dict
        with three sub-keys:

        * ``added`` — keys present in *b* but not in *a*.
        * ``removed`` — keys present in *a* but not in *b*.
        * ``changed`` — keys present in both but with different values.

        Args:
            commit_a: SHA-256 commit ID of the *before* state.
            commit_b: SHA-256 commit ID of the *after* state.

        Returns:
            Dict with ``added``, ``removed``, and ``changed`` sub-dicts.

        Raises:
            KeyError: If either commit ID is not found in the store.
        """
        data_a = self._fetch_config_data(commit_a)
        data_b = self._fetch_config_data(commit_b)

        flat_a = _flatten(data_a)
        flat_b = _flatten(data_b)

        keys_a = set(flat_a)
        keys_b = set(flat_b)

        added = {k: flat_b[k] for k in keys_b - keys_a}
        removed = {k: flat_a[k] for k in keys_a - keys_b}
        changed = {
            k: {"before": flat_a[k], "after": flat_b[k]}
            for k in keys_a & keys_b
            if flat_a[k] != flat_b[k]
        }
        return {"added": added, "removed": removed, "changed": changed}

    def rollback_config(self, study_key: str, commit_id: str) -> StudyConfiguration:
        """Restore and return the ``StudyConfiguration`` stored at *commit_id*.

        This method is non-destructive — it does not modify any existing
        history rows.  The caller is responsible for creating a new commit via
        :meth:`commit_config` if they wish to record the rollback.

        Args:
            study_key: The study the commit must belong to.
            commit_id: The SHA-256 commit ID to restore.

        Returns:
            The deserialised ``StudyConfiguration``.

        Raises:
            KeyError: If the commit is not found or does not belong to the
                requested study.
        """
        with self._lock, self._connection() as conn:
            row = conn.execute(
                """
                SELECT commit_id, config_data
                FROM config_commits
                WHERE commit_id = ? AND study_key = ?
                """,
                (commit_id, study_key),
            ).fetchone()
        if row is None:
            raise KeyError(f"Commit {commit_id!r} not found for study {study_key!r}.")
        self._verify_commit_signature(row["commit_id"], row["config_data"])
        return StudyConfiguration.model_validate_json(row["config_data"])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_config_data(self, commit_id: str) -> dict[str, Any]:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                "SELECT commit_id, config_data FROM config_commits WHERE commit_id = ?",
                (commit_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Commit {commit_id!r} not found.")
        self._verify_commit_signature(row["commit_id"], row["config_data"])
        return json.loads(row["config_data"])  # type: ignore[no-any-return]

    def _verify_commit_signature(self, commit_id: str, config_data: str) -> None:
        if _sha256_of(config_data) != commit_id:
            raise ValueError(
                "Configuration data integrity check failed: "
                f"SHA-256 hash mismatch for commit {commit_id!r}"
            )


def _flatten(data: Any, prefix: str = "") -> dict[str, Any]:
    """Recursively flatten a nested dict/list into dot-notation keys."""
    result: dict[str, Any] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            result.update(_flatten(value, full_key))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            full_key = f"{prefix}[{index}]"
            result.update(_flatten(item, full_key))
    else:
        result[prefix] = data
    return result


__all__ = ["ConfigVersionStore"]
