from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from imednet.core import exceptions
from imednet.core.async_client import AsyncClient


@pytest.mark.asyncio
async def test_async_request_retries(monkeypatch):
    client = AsyncClient("k", "s", base_url="https://api.test", retries=2)
    calls = {"count": 0}

    async def request(method, url, **kw):
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.RequestError("boom", request=httpx.Request(method, url))
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(client._client, "request", request)
    resp = await client.get("/path")
    assert resp.status_code == 200
    assert calls["count"] == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,exc",
    [
        (400, exceptions.ValidationError),
        (401, exceptions.AuthenticationError),
        (403, exceptions.AuthorizationError),
        (404, exceptions.NotFoundError),
        (429, exceptions.RateLimitError),
        (500, exceptions.ServerError),
        (418, exceptions.ApiError),
    ],
)
async def test_async_request_error_mapping(monkeypatch, status, exc):
    client = AsyncClient("k", "s", base_url="https://api.test")

    async def request(method, url, **kw):
        return httpx.Response(status, json={"error": status})

    monkeypatch.setattr(client._client, "request", request)
    with pytest.raises(exc):
        await client.get("/some")


@pytest.mark.asyncio
async def test_tracing(monkeypatch):
    tracer = MagicMock()
    span_cm = AsyncMock()
    span = MagicMock()
    span_cm.__aenter__.return_value = span
    tracer.start_as_current_span.return_value = span_cm

    client = AsyncClient("k", "s", base_url="https://api.test", tracer=tracer)
    monkeypatch.setattr(client._client, "request", AsyncMock(return_value=httpx.Response(200)))

    await client.get("/trace")

    tracer.start_as_current_span.assert_called_with(
        "http_request", attributes={"endpoint": "/trace", "method": "GET"}
    )
    span.set_attribute.assert_called_with("status_code", 200)
