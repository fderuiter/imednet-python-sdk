"""Encrypted credential storage for iMednet SDK supporting multiple studies."""

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


def _decrypt(data: bytes, password: str) -> list[dict[str, str]]:
    fernet = Fernet(_derive_key(password))
    decrypted = fernet.decrypt(data)
    return json.loads(decrypted.decode())


def _encrypt(creds: list[dict[str, str]], password: str) -> bytes:
    fernet = Fernet(_derive_key(password))
    return fernet.encrypt(json.dumps(creds).encode())


def _load(password: str, path: Path | None = None) -> list[dict[str, str]]:
    target = path or CREDENTIALS_FILE
    if not target.exists():
        return []
    return _decrypt(target.read_bytes(), password)


def _save(creds: list[dict[str, str]], password: str, path: Path | None = None) -> None:
    target = path or CREDENTIALS_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(_encrypt(creds, password))


def save_credentials(
    api_key: str,
    security_key: str,
    study_key: str,
    study_name: str,
    password: str,
    path: Path | None = None,
) -> None:
    """Save or update credentials for a study."""
    creds = _load(password, path)
    creds = [c for c in creds if c["study_key"] != study_key]
    creds.append(
        {
            "api_key": api_key,
            "security_key": security_key,
            "study_key": study_key,
            "study_name": study_name,
        }
    )
    _save(creds, password, path)


def list_credentials(
    password: Optional[str] = None, path: Path | None = None
) -> list[dict[str, str]]:
    """Return all stored credentials."""
    pwd = password or os.getenv("IMEDNET_CRED_PASSWORD")
    if not pwd:
        return []
    try:
        return _load(pwd, path)
    except Exception:
        return []


def resolve_credentials(
    study_key: Optional[str] = None, password: Optional[str] = None
) -> tuple[str, str, str]:
    """Return API credentials from environment or stored credentials."""
    api_key = os.getenv("IMEDNET_API_KEY")
    security_key = os.getenv("IMEDNET_SECURITY_KEY")
    if not study_key:
        study_key = os.getenv("IMEDNET_STUDY_KEY")

    stored = list_credentials(password)
    cred: Optional[dict[str, str]] = None
    if study_key:
        cred = next((c for c in stored if c["study_key"] == study_key), None)
    if cred is None and stored:
        cred = stored[0]
    if cred:
        api_key = api_key or cred["api_key"]
        security_key = security_key or cred["security_key"]
        study_key = study_key or cred["study_key"]

    if not api_key or not security_key or not study_key:
        raise RuntimeError("iMednet credentials not found in environment or storage")

    return api_key, security_key, study_key
