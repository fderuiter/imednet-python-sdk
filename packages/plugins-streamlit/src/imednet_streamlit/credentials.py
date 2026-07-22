"""Thread-safe credential management repository."""

import logging
import os
import sqlite3
import threading

_db_lock = threading.Lock()
logger = logging.getLogger(__name__)


class CredentialRepository:
    """Manages secure access to tenant credentials in a local SQLite database."""

    def __init__(self, db_path: str):
        """Initialize the repository with a path to the database.

        Args:
            db_path: The filesystem path to the SQLite database.
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Ensure the database and tables exist with the correct schema."""
        with _db_lock:
            if not os.path.exists(self.db_path):
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS tenants (study_key TEXT PRIMARY KEY, api_key TEXT, security_key TEXT)"
                )
                cursor = conn.execute("PRAGMA table_info(tenants)")
                columns = [row[1] for row in cursor.fetchall()]
                if "env_url" not in columns:
                    conn.execute("ALTER TABLE tenants ADD COLUMN env_url TEXT")

    def get_credentials(self, study_key: str) -> tuple[str | None, str | None, str | None]:
        """Retrieve credentials for a given study key.

        Args:
            study_key: The study key to lookup.

        Returns:
            A tuple of (api_key, security_key, env_url), or (None, None, None) if not found.
        """
        with _db_lock:
            if not os.path.exists(self.db_path):
                return None, None, None
            try:
                with sqlite3.connect(self.db_path) as conn:
                    row = conn.execute(
                        "SELECT api_key, security_key, env_url FROM tenants WHERE study_key=?",
                        (study_key,),
                    ).fetchone()
                    if row:
                        return row[0], row[1], row[2]
            except Exception as e:
                logger.error("Failed to read credentials: %s", e)
            return None, None, None

    def get_provisioned_studies(self) -> list[str]:
        """Get a list of all provisioned study keys.

        Returns:
            A list of study keys.
        """
        with _db_lock:
            if not os.path.exists(self.db_path):
                return []
            try:
                with sqlite3.connect(self.db_path) as conn:
                    return [row[0] for row in conn.execute("SELECT study_key FROM tenants")]
            except sqlite3.OperationalError:
                return []

    def provision_tenant(
        self, study_key: str, api_key: str, security_key: str, env_url: str | None = None
    ):
        """Provision or update credentials for a tenant.

        Args:
            study_key: The study key identifier.
            api_key: The API key for the tenant.
            security_key: The security key for the tenant.
            env_url: Optional base URL for the tenant's environment.
        """
        with _db_lock:
            if not os.path.exists(self.db_path):
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS tenants (study_key TEXT PRIMARY KEY, api_key TEXT, security_key TEXT)"
                )
                cursor = conn.execute("PRAGMA table_info(tenants)")
                columns = [row[1] for row in cursor.fetchall()]
                if "env_url" not in columns:
                    conn.execute("ALTER TABLE tenants ADD COLUMN env_url TEXT")

                conn.execute(
                    "INSERT OR REPLACE INTO tenants (study_key, api_key, security_key, env_url) VALUES (?, ?, ?, ?)",
                    (
                        study_key.strip(),
                        api_key.strip(),
                        security_key.strip(),
                        env_url.strip() if env_url and env_url.strip() else None,
                    ),
                )
