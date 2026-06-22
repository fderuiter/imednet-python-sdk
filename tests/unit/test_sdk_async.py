"""TODO: Add docstring."""
import pytest

from imednet import sdk as sdk_mod
from imednet.core.async_client import AsyncClient


def _create_async_sdk() -> sdk_mod.AsyncImednetSDK:
    """TODO: Add docstring."""
    return sdk_mod.AsyncImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )


def test_async_sdk_initializes_async_client() -> None:
    """TODO: Add docstring."""
    sdk = _create_async_sdk()
    assert isinstance(sdk._async_client, AsyncClient)


def test_async_sdk_is_not_subclass_of_sync_sdk() -> None:
    """TODO: Add docstring."""
    assert not issubclass(sdk_mod.AsyncImednetSDK, sdk_mod.ImednetSDK)


def test_sync_and_async_endpoints_expose_strict_method_surfaces() -> None:
    """TODO: Add docstring."""
    sync_sdk = sdk_mod.ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )
    async_sdk = _create_async_sdk()

    assert hasattr(sync_sdk.sites, "list")
    assert hasattr(sync_sdk.sites, "get")
    assert not hasattr(sync_sdk.sites, "async_list")
    assert not hasattr(sync_sdk.sites, "async_get")

    assert hasattr(async_sdk.sites, "async_list")
    assert hasattr(async_sdk.sites, "async_get")
    assert not hasattr(async_sdk.sites, "list")
    assert not hasattr(async_sdk.sites, "get")


@pytest.mark.asyncio
async def test_async_context_management(monkeypatch) -> None:
    """TODO: Add docstring."""
    called = {"close": False}

    async def fake_aclose(self) -> None:
        """TODO: Add docstring."""
        called["close"] = True

    monkeypatch.setattr(AsyncClient, "aclose", fake_aclose)

    async with _create_async_sdk() as sdk:
        assert isinstance(sdk, sdk_mod.AsyncImednetSDK)

    assert called["close"]


@pytest.mark.asyncio
async def test_convenience_methods_delegate_to_endpoints_async(monkeypatch) -> None:
    """TODO: Add docstring."""
    sdk = _create_async_sdk()
    calls = {}

    async def fake_async_studies_list(**kw):
        """TODO: Add docstring."""
        calls["studies"] = kw
        return ["STUDY"]

    monkeypatch.setattr(sdk.studies, "async_list", fake_async_studies_list)

    assert await sdk.async_get_studies(status="active") == ["STUDY"]
    assert calls["studies"] == {"status": "active"}
