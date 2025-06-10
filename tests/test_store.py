from __future__ import annotations

import importlib
import stat
from pathlib import Path

import keyring
import pytest


def test_round_trip_and_permissions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # patch Path.home before importing store module
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from imednet.utils import store

    importlib.reload(store)

    backend = DummyBackend()
    keyring.set_keyring(backend)

    # simulate keyring failure to trigger file fallback
    def fail(*_a: object, **_kw: object) -> None:
        raise keyring.errors.KeyringError()

    monkeypatch.setattr(keyring, "set_password", fail)
    monkeypatch.setattr(keyring, "get_password", fail)

    store.save_secret("foo", "bar")
    assert store.load_secret("foo") == "bar"

    secret_file = store.CONFIG_ROOT / "secrets.enc"
    if secret_file.exists():
        mode = stat.S_IMODE(secret_file.stat().st_mode)
        assert mode == 0o600


class DummyBackend(keyring.backend.KeyringBackend):
    priority = 1

    def __init__(self) -> None:
        self.store: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, username: str) -> str | None:
        return self.store.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        self.store[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:  # pragma: no cover
        self.store.pop((service, username), None)
