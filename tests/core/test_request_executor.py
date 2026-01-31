import httpx
import pytest
import respx

from imednet.core.exceptions import NotFoundError
from imednet.core.request_executor import RequestExecutor


@respx.mock
def test_sync_executor_retries_success():
    client = httpx.Client(base_url="https://api.test")
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.RequestError("boom", request=request)
        return httpx.Response(200, json={"ok": True})

    respx.get("https://api.test/ping").mock(side_effect=handler)

    executor = RequestExecutor(client.request, is_async=False, retries=2, backoff_factor=0)
    resp = executor("GET", "/ping")
    assert resp.status_code == 200
    assert calls["count"] == 2
    client.close()


@respx.mock
@pytest.mark.asyncio
async def test_async_executor_error_mapping():
    async_client = httpx.AsyncClient(base_url="https://api.test")
    respx.get("https://api.test/bad").respond(status_code=404, json={"msg": "x"})

    executor = RequestExecutor(async_client.request, is_async=True, retries=1, backoff_factor=0)

    with pytest.raises(NotFoundError):
        try:
            await executor("GET", "/bad")
        finally:
            await async_client.aclose()
