import asyncio

import httpx

from imednet.core.client import AsyncClient


class DummyAsyncHTTPClient:
    def __init__(self, *args, **kwargs):
        self.request_calls = []

    async def request(self, method: str, url: str, **kwargs):
        self.request_calls.append((method, url, kwargs))
        return httpx.Response(200, json={"ok": True})

    async def aclose(self) -> None:
        pass


def test_async_client_get(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncHTTPClient)
    client = AsyncClient(api_key="k", security_key="s", base_url="http://test")

    async def run():
        resp = await client.get("/foo")
        assert resp.json() == {"ok": True}
        await client.close()

    asyncio.run(run())
