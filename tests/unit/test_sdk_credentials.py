import pytest

from imednet.config import Config
from imednet.sdk import ImednetSDK


def test_missing_both_keys(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="", security_key="", base_url=None),
    )
    with pytest.raises(
        ValueError,
        match="IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set.",
    ):
        ImednetSDK()


def test_missing_security_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="key", security_key="", base_url=None),
    )
    with pytest.raises(ValueError, match="IMEDNET_SECURITY_KEY is required"):
        ImednetSDK()


def test_missing_api_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="", security_key="sec", base_url=None),
    )
    with pytest.raises(ValueError, match="IMEDNET_API_KEY is required"):
        ImednetSDK()


def test_initialization_succeeds(monkeypatch) -> None:
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="key", security_key="sec", base_url=None),
    )
    sdk = ImednetSDK()
    assert isinstance(sdk, ImednetSDK)
