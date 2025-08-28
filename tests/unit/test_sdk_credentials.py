import pytest

from imednet.config import Config
from imednet.sdk import ImednetSDK


def test_missing_both_keys(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config_from_env",
        lambda **_: Config(api_key="", security_key="", base_url=None),
    )
    with pytest.raises(ValueError, match="API key and security key are required"):
        ImednetSDK()


def test_missing_security_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config_from_env",
        lambda **_: Config(api_key="key", security_key="", base_url=None),
    )
    with pytest.raises(ValueError, match="Security key is required"):
        ImednetSDK()


def test_missing_api_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config_from_env",
        lambda **_: Config(api_key="", security_key="sec", base_url=None),
    )
    with pytest.raises(ValueError, match="API key is required"):
        ImednetSDK()


def test_initialization_succeeds(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config_from_env",
        lambda **_: Config(api_key="key", security_key="sec", base_url=None),
    )
    sdk = ImednetSDK()
    assert isinstance(sdk, ImednetSDK)
