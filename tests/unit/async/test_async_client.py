import httpx
import pytest
from imednet.core.async_client import AsyncClient
from imednet.core.base_client import BaseClient


def test_async_client_subclass() -> None:
    assert issubclass(AsyncClient, BaseClient)


@pytest.mark.asyncio
async def test_get_request(respx_mock):
    client = AsyncClient("key", "secret", base_url="https://api.test")
    respx_mock.base_url = client.base_url
    respx_mock.get("/ping").mock(return_value=httpx.Response(200, json={"ok": True}))

    resp = await client.get("/ping")
    await client.aclose()

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
