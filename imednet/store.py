from __future__ import annotations

import json
from pathlib import Path

import keyring
from cryptography.fernet import Fernet


class SecretStoreError(Exception):
    """Raised when saving or loading a secret fails."""


CONFIG_ROOT = Path.home() / ".medveeva"
CONFIG_ROOT.mkdir(mode=0o700, exist_ok=True)

_SECRETS_FILE = CONFIG_ROOT / "secrets.enc"
_KEY_FILE = CONFIG_ROOT / "secrets.key"
_FERNET_KEYRING_NAME = "fernet_key"


def _get_fernet() -> Fernet:
    try:
        key = keyring.get_password("medveeva", _FERNET_KEYRING_NAME)
        if key:
            return Fernet(key.encode())
    except Exception:
        pass

    if _KEY_FILE.exists():
        key_bytes = _KEY_FILE.read_bytes()
    else:
        key_bytes = Fernet.generate_key()
        try:
            keyring.set_password("medveeva", _FERNET_KEYRING_NAME, key_bytes.decode())
        except Exception:
            _KEY_FILE.write_bytes(key_bytes)
            _KEY_FILE.chmod(0o600)
    return Fernet(key_bytes)


def _save_file_secret(name: str, value: str) -> None:
    fernet = _get_fernet()
    data: dict[str, str] = {}
    if _SECRETS_FILE.exists():
        token = _SECRETS_FILE.read_bytes()
        if token:
            decrypted = fernet.decrypt(token)
            data = json.loads(decrypted.decode("utf-8"))
    data[name] = value
    token = fernet.encrypt(json.dumps(data).encode("utf-8"))
    _SECRETS_FILE.write_bytes(token)
    _SECRETS_FILE.chmod(0o600)


def _load_file_secret(name: str) -> str | None:
    if not _SECRETS_FILE.exists():
        return None
    fernet = _get_fernet()
    token = _SECRETS_FILE.read_bytes()
    if not token:
        return None
    data = json.loads(fernet.decrypt(token).decode("utf-8"))
    return data.get(name)


def save_secret(name: str, value: str) -> None:
    try:
        keyring.set_password("medveeva", name, value)
        return
    except Exception:
        pass

    try:
        _save_file_secret(name, value)
    except Exception as exc:  # pragma: no cover - shouldn't happen in tests
        raise SecretStoreError(str(exc)) from exc


def load_secret(name: str) -> str | None:
    try:
        value = keyring.get_password("medveeva", name)
        if value is not None:
            return value
    except Exception:
        pass

    try:
        return _load_file_secret(name)
    except Exception as exc:  # pragma: no cover - shouldn't happen in tests
        raise SecretStoreError(str(exc)) from exc
