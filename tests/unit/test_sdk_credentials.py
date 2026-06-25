"""Tests for test_sdk_credentials."""

import pytest

from imednet.config import Config
from imednet.sdk import ImednetSDK


def test_missing_both_keys(monkeypatch) -> None:
    """Test test_missing_both_keys behavior."""
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="", security_key="", base_url=None),
    )
    with pytest.raises(ValueError, match="API key and security key are required"):
        ImednetSDK()


def test_missing_security_key(monkeypatch) -> None:
    """Test test_missing_security_key behavior."""
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="key", security_key="", base_url=None),
    )
    with pytest.raises(ValueError, match="Security key is required"):
        ImednetSDK()


def test_missing_api_key(monkeypatch) -> None:
    """Test test_missing_api_key behavior."""
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="", security_key="sec", base_url=None),
    )
    with pytest.raises(ValueError, match="API key is required"):
        ImednetSDK()


def test_initialization_succeeds(monkeypatch) -> None:
    """Test test_initialization_succeeds behavior."""
    monkeypatch.setattr(
        "imednet.sdk.load_config",
        lambda **_: Config(api_key="key", security_key="sec", base_url=None),
    )
    sdk = ImednetSDK()
    assert isinstance(sdk, ImednetSDK)
