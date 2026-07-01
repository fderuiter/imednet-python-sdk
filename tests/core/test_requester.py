"""Unit tests for requester."""

import httpx
import pytest
import respx
from tenacity import RetryError

from imednet.core.http.executor import AsyncRequestExecutor, SyncRequestExecutor
from imednet.errors import NotFoundError, RequestError, ServerError


@respx.mock
def test_sync_executor_retries_success():
    """Test that sync executor retries success."""
    client = httpx.Client(base_url="https://api.test")
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        """Helper function to handler."""
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.RequestError("boom", request=request)
        return httpx.Response(200, json={"ok": True})

    respx.get("https://api.test/ping").mock(side_effect=handler)

    executor = SyncRequestExecutor(client.request, retries=2, backoff_factor=0)
    resp = executor("GET", "/ping")
    assert resp.status_code == 200
    assert calls["count"] == 2
    client.close()


@respx.mock
@pytest.mark.asyncio
async def test_async_executor_error_mapping():
    """Test that async executor error mapping asynchronously."""
    async_client = httpx.AsyncClient(base_url="https://api.test")
    respx.get("https://api.test/bad").respond(status_code=404, json={"msg": "x"})

    executor = AsyncRequestExecutor(async_client.request, retries=1, backoff_factor=0)

    with pytest.raises(NotFoundError):
        try:
            await executor("GET", "/bad")
        finally:
            await async_client.aclose()


@respx.mock
def test_sync_executor_retries_exhausted():
    """Test that sync executor retries exhausted."""
    client = httpx.Client(base_url="https://api.test")
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        """Helper function to handler."""
        calls["count"] += 1
        raise httpx.RequestError("boom", request=request)

    respx.get("https://api.test/ping").mock(side_effect=handler)

    executor = SyncRequestExecutor(client.request, retries=2, backoff_factor=0)

    with pytest.raises(RequestError, match="Network request failed after retries"):
        executor("GET", "/ping")

    assert calls["count"] == 3
    client.close()


@respx.mock
def test_sync_executor_retries_exhausted_with_error_response():
    """Test that sync executor retries exhausted with error response."""
    client = httpx.Client(base_url="https://api.test")
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        """Helper function to handler."""
        calls["count"] += 1
        return httpx.Response(500, json={"error": "server error"})

    respx.get("https://api.test/ping").mock(side_effect=handler)

    executor = SyncRequestExecutor(client.request, retries=2, backoff_factor=0)

    with pytest.raises(ServerError):
        executor("GET", "/ping")

    assert calls["count"] == 3
    client.close()


@respx.mock
@pytest.mark.asyncio
async def test_async_executor_retries_exhausted():
    """Test that async executor retries exhausted asynchronously."""
    async_client = httpx.AsyncClient(base_url="https://api.test")
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        """Helper function to handler."""
        calls["count"] += 1
        raise httpx.RequestError("boom", request=request)

    respx.get("https://api.test/ping").mock(side_effect=handler)

    executor = AsyncRequestExecutor(async_client.request, retries=2, backoff_factor=0)

    with pytest.raises(RequestError, match="Network request failed after retries"):
        try:
            await executor("GET", "/ping")
        finally:
            await async_client.aclose()

    assert calls["count"] == 3


@respx.mock
def test_sync_executor_null_response(monkeypatch):
    """Test that sync executor null response."""
    client = httpx.Client(base_url="https://api.test")

    def mock_retryer(*args, **kwargs):
        """Helper function to mock retryer."""
        return None

    monkeypatch.setattr("tenacity.Retrying.__call__", mock_retryer)

    executor = SyncRequestExecutor(client.request, retries=0, backoff_factor=0)

    with pytest.raises(RuntimeError, match="Request failed without response or exception"):
        executor("GET", "/ping")

    client.close()


@respx.mock
@pytest.mark.asyncio
async def test_async_executor_null_response(monkeypatch):
    """Test that async executor null response asynchronously."""
    async_client = httpx.AsyncClient(base_url="https://api.test")

    async def mock_retryer(*args, **kwargs):
        """Helper function to mock retryer."""
        return None

    monkeypatch.setattr("tenacity.AsyncRetrying.__call__", mock_retryer)

    executor = AsyncRequestExecutor(async_client.request, retries=0, backoff_factor=0)

    with pytest.raises(RuntimeError, match="Request failed without response or exception"):
        try:
            await executor("GET", "/ping")
        finally:
            await async_client.aclose()


@respx.mock
@pytest.mark.asyncio
async def test_async_executor_retries_exhausted_with_error_response():
    """Test that async executor retries exhausted with error response asynchronously."""
    async_client = httpx.AsyncClient(base_url="https://api.test")
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        """Helper function to handler."""
        calls["count"] += 1
        return httpx.Response(500, json={"error": "server error"})

    respx.get("https://api.test/ping").mock(side_effect=handler)

    executor = AsyncRequestExecutor(async_client.request, retries=2, backoff_factor=0)

    with pytest.raises(ServerError):
        try:
            await executor("GET", "/ping")
        finally:
            await async_client.aclose()

    assert calls["count"] == 3


class FakeAttempt:
    """Test suite for FakeAttempt."""

    def __init__(self, failed):
        """Initialize the test object."""
        self.failed = failed

    def exception(self):
        """Helper function to exception."""
        return RuntimeError("Fake error")

    def result(self):
        """Helper function to result."""
        return httpx.Response(200, json={"ok": True})


class FakeRetryError(RetryError):
    """Test suite for FakeRetryError."""

    def __init__(self, failed):
        """Initialize the test object."""
        self.last_attempt = FakeAttempt(failed)
        super().__init__(self.last_attempt)


def test_sync_executor_unreachable_branch(monkeypatch):
    """Test that sync executor unreachable branch."""
    client = httpx.Client(base_url="https://api.test")

    def mock_retryer(*args, **kwargs):
        """Helper function to mock retryer."""
        raise FakeRetryError(False)

    monkeypatch.setattr("tenacity.Retrying.__call__", mock_retryer)

    executor = SyncRequestExecutor(client.request, retries=0, backoff_factor=0)

    resp = executor("GET", "/ping")
    assert resp.status_code == 200

    client.close()


@pytest.mark.asyncio
async def test_async_executor_unreachable_branch(monkeypatch):
    """Test that async executor unreachable branch asynchronously."""
    async_client = httpx.AsyncClient(base_url="https://api.test")

    async def mock_retryer(*args, **kwargs):
        """Helper function to mock retryer."""
        raise FakeRetryError(False)

    monkeypatch.setattr("tenacity.AsyncRetrying.__call__", mock_retryer)

    executor = AsyncRequestExecutor(async_client.request, retries=0, backoff_factor=0)

    resp = await executor("GET", "/ping")
    assert resp.status_code == 200

    await async_client.aclose()
