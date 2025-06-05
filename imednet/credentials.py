"""Encrypted credential storage for iMednet SDK."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet

CREDENTIALS_FILE = Path.home() / ".imednet" / "credentials.enc"


def _derive_key(password: str) -> bytes:
    """Derive a Fernet key from the provided password."""
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def save_credentials(
    api_key: str,
    security_key: str,
    study_key: str,
    password: str,
    path: Path | None = None,
) -> None:
    """Encrypt and save credentials to disk."""
    target = path or CREDENTIALS_FILE
    target.parent.mkdir(parents=True, exist_ok=True)

    creds = {"api_key": api_key, "security_key": security_key, "study_key": study_key}
    data = json.dumps(creds).encode()
    fernet = Fernet(_derive_key(password))
    encrypted = fernet.encrypt(data)
    with open(target, "wb") as f:
        f.write(encrypted)


def load_credentials(password: str, path: Path | None = None) -> dict[str, str]:
    """Load and decrypt credentials from disk."""
    target = path or CREDENTIALS_FILE
    data = target.read_bytes()
    fernet = Fernet(_derive_key(password))
    decrypted = fernet.decrypt(data)
    return json.loads(decrypted.decode())


def get_stored_credentials(password: Optional[str] = None) -> Optional[dict[str, str]]:
    """Return saved credentials if available and password provided."""
    if not CREDENTIALS_FILE.exists() or not password:
        return None
    try:
        return load_credentials(password)
    except Exception:
        return None


def resolve_credentials(password: Optional[str] = None) -> tuple[str, str, Optional[str]]:
    """Return API credentials from environment or encrypted storage."""
    api_key = os.getenv("IMEDNET_API_KEY")
    security_key = os.getenv("IMEDNET_SECURITY_KEY")
    study_key = os.getenv("IMEDNET_STUDY_KEY")

    stored = None
    if not api_key or not security_key or study_key is None:
        stored = get_stored_credentials(password or os.getenv("IMEDNET_CRED_PASSWORD"))
    if stored:
        api_key = api_key or stored.get("api_key")
        security_key = security_key or stored.get("security_key")
        study_key = study_key or stored.get("study_key")

    if not api_key or not security_key:
        raise RuntimeError("iMednet credentials not found in environment or storage")

    return api_key, security_key, study_key
