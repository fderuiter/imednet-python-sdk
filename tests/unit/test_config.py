import pytest

from imednet.config import Config, load_config


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("IMEDNET_API_KEY", "env_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_secret")
    monkeypatch.setenv("IMEDNET_BASE_URL", " https://example.com ")

    cfg = load_config()
    assert cfg == Config(
        api_key="env_key", security_key="env_secret", base_url="https://example.com"
    )


def test_load_config_overrides_env(monkeypatch):
    monkeypatch.setenv("IMEDNET_API_KEY", "env_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_secret")
    cfg = load_config(api_key="arg_key", security_key="arg_sec", base_url="https://override")
    assert cfg == Config(api_key="arg_key", security_key="arg_sec", base_url="https://override")


def test_load_config_missing(monkeypatch):
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)
    with pytest.raises(ValueError):
        load_config()
