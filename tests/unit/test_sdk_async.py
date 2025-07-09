import pytest

from imednet import sdk as sdk_mod
from imednet.core.async_client import AsyncClient


def _create_async_sdk() -> sdk_mod.ImednetSDK:
    return sdk_mod.ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
        enable_async=True,
    )


def test_async_sdk_initializes_async_client() -> None:
    sdk = _create_async_sdk()
    assert isinstance(sdk._async_client, AsyncClient)


@pytest.mark.asyncio
async def test_async_context_management(monkeypatch) -> None:
    called = {"close": False}

    async def fake_aclose(self) -> None:
        called["close"] = True

    monkeypatch.setattr(AsyncClient, "aclose", fake_aclose)

    async with _create_async_sdk() as sdk:
        assert isinstance(sdk, sdk_mod.ImednetSDK)

    assert called["close"]
