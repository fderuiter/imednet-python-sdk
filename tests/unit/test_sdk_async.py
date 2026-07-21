"""Unit tests for sdk async."""

import pytest

from imednet import sdk as sdk_mod
from imednet.core.async_client import AsyncClient


def _create_async_sdk() -> sdk_mod.AsyncImednetSDK:
    """Helper function to  create async sdk."""
    return sdk_mod.AsyncImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )


def test_async_sdk_initializes_async_client() -> None:
    """Test that async sdk initializes async client."""
    sdk = _create_async_sdk()
    assert isinstance(sdk._async_client, AsyncClient)


def test_async_sdk_is_not_subclass_of_sync_sdk() -> None:
    """Test that async sdk is not subclass of sync sdk."""
    assert not issubclass(sdk_mod.AsyncImednetSDK, sdk_mod.ImednetSDK)


def test_sync_and_async_endpoints_expose_strict_method_surfaces() -> None:
    """Test that sync and async endpoints expose strict method surfaces."""
    sync_sdk = sdk_mod.ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )
    async_sdk = _create_async_sdk()

    assert hasattr(sync_sdk.sites, "list")
    assert hasattr(sync_sdk.sites, "get")
    assert not hasattr(sync_sdk.sites, "async_list")
    assert hasattr(async_sdk.sites, "list")
    assert hasattr(async_sdk.sites, "get")
    assert hasattr(async_sdk.sites, "list")
    assert hasattr(async_sdk.sites, "get")
    assert not hasattr(sync_sdk.sites, "async_get")

    assert not hasattr(async_sdk.sites, "async_list")
    assert not hasattr(async_sdk.sites, "async_get")


@pytest.mark.asyncio
async def test_async_context_management(monkeypatch) -> None:
    """Test that async context management asynchronously."""
    called = {"close": False}

    async def fake_aclose(self) -> None:
        """Helper function to fake aclose."""
        called["close"] = True

    monkeypatch.setattr(AsyncClient, "aclose", fake_aclose)

    async with _create_async_sdk() as sdk:
        assert isinstance(sdk, sdk_mod.AsyncImednetSDK)

    assert called["close"]


@pytest.mark.asyncio
async def test_convenience_methods_delegate_to_endpoints_async(monkeypatch) -> None:
    """Test that convenience methods delegate to endpoints async asynchronously."""
    sdk = _create_async_sdk()
    calls = {}

    async def fake_studies_list(**kw):
        """Helper function to fake async studies list."""
        calls["studies"] = kw
        return ["STUDY"]

    monkeypatch.setattr(sdk.studies, "list", fake_studies_list)

    assert await sdk.async_get_studies(status="active") == ["STUDY"]
    assert calls["studies"] == {"status": "active"}
