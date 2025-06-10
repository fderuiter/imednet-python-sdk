from __future__ import annotations

import stat

from imednet import store


def test_save_and_load_secret(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONFIG_ROOT", tmp_path)
    monkeypatch.setattr(store, "_SECRETS_FILE", tmp_path / "secrets.enc")
    monkeypatch.setattr(store, "_KEY_FILE", tmp_path / "secrets.key")

    def fail(*args, **kwargs):
        raise RuntimeError("no keyring")

    monkeypatch.setattr(store.keyring, "set_password", fail)
    monkeypatch.setattr(store.keyring, "get_password", fail)

    store.save_secret("dummy", "value")
    assert store.load_secret("dummy") == "value"
    mode = stat.S_IMODE((tmp_path / "secrets.enc").stat().st_mode)
    assert mode == 0o600
