from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import keyring
from cryptography.fernet import Fernet, InvalidToken


class SecretStoreError(Exception):
    """Raised when saving or loading secrets fails."""


CONFIG_ROOT = Path.home() / ".medveeva"
CONFIG_ROOT.mkdir(mode=0o700, exist_ok=True)

_SERVICE = "medveeva"
_KEY_NAME = "fernet_key"
_SECRETS_FILE = CONFIG_ROOT / "secrets.enc"
_KEY_FILE = CONFIG_ROOT / "secrets.key"


def _get_fernet() -> Fernet:
    key: Optional[str] = None
    try:
        key = keyring.get_password(_SERVICE, _KEY_NAME)
    except Exception:
        key = None

    if key is None and _KEY_FILE.exists():
        key = _KEY_FILE.read_text()

    if key is None:
        key = Fernet.generate_key().decode()
        stored = False
        try:
            keyring.set_password(_SERVICE, _KEY_NAME, key)
            stored = True
        except Exception:
            stored = False
        if not stored:
            _KEY_FILE.write_text(key)
            os.chmod(_KEY_FILE, 0o600)

    return Fernet(key.encode())


def _load_file_secrets(f: Fernet) -> dict[str, str]:
    if not _SECRETS_FILE.exists():
        return {}
    token = _SECRETS_FILE.read_bytes()
    try:
        data = f.decrypt(token)
    except InvalidToken as exc:  # pragma: no cover - corrupted file
        raise SecretStoreError("Invalid secrets file") from exc
    return json.loads(data.decode())


def _save_file_secrets(f: Fernet, secrets: dict[str, str]) -> None:
    token = f.encrypt(json.dumps(secrets).encode())
    _SECRETS_FILE.write_bytes(token)
    os.chmod(_SECRETS_FILE, 0o600)


def save_secret(name: str, value: str) -> None:
    """Save a secret value identified by ``name``."""
    try:
        keyring.set_password(_SERVICE, name, value)
        return
    except Exception:
        pass

    f = _get_fernet()
    secrets = _load_file_secrets(f)
    secrets[name] = value
    _save_file_secrets(f, secrets)


def load_secret(name: str) -> Optional[str]:
    """Load a previously saved secret."""
    try:
        return keyring.get_password(_SERVICE, name)
    except Exception:
        pass

    if not _SECRETS_FILE.exists():
        return None
    f = _get_fernet()
    secrets = _load_file_secrets(f)
    return secrets.get(name)
