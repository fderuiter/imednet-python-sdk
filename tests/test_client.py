import pytest

from imednet_py.client import ImednetClient


def test_session_headers() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    assert client.session.headers["x-api-key"] == "key"
    assert client.session.headers["x-imn-security-key"] == "sec"
    assert client.base_url == "https://edc.prod.imednetapi.com/api/v1/edc/"


def test_env_var_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "env_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_sec")
    client = ImednetClient()
    assert client.session.headers["x-api-key"] == "env_key"
    assert client.session.headers["x-imn-security-key"] == "env_sec"


def test_missing_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)
    with pytest.raises(ValueError):
        ImednetClient()
