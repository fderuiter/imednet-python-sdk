"""Tests for test_retry."""

from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from imednet.core.http.executor import AsyncRequestExecutor, SyncRequestExecutor
from imednet.errors import RequestError


def test_retry_exhaustion_sync():
    """Verify that RequestError is raised after retries are exhausted in sync mode."""
    # httpx.ConnectError instantiation might need request/url depending on version
    # But usually message is enough for simple tests
    mock_send = Mock(side_effect=httpx.ConnectError("Connection failed"))

    executor = SyncRequestExecutor(send=mock_send, retries=2, backoff_factor=0.01)

    with pytest.raises(RequestError) as exc_info:
        executor("GET", "http://test.com")

    assert "Network request failed after retries" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)
    assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_retry_exhaustion_async():
    """Verify that RequestError is raised after retries are exhausted in async mode."""
    mock_send = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

    executor = AsyncRequestExecutor(send=mock_send, retries=2, backoff_factor=0.01)

    with pytest.raises(RequestError) as exc_info:
        await executor("GET", "http://test.com")

    assert "Network request failed after retries" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)
    assert mock_send.call_count == 2


@pytest.mark.parametrize("method", ["POST", "PATCH"])
def test_non_idempotent_method_does_not_retry_on_connect_error_sync(method: str):
    """Non-idempotent methods must not retry on network errors (sync)."""
    mock_send = Mock(side_effect=httpx.ConnectError("Connection failed"))

    executor = SyncRequestExecutor(send=mock_send, retries=3, backoff_factor=0.01)

    with pytest.raises(httpx.ConnectError):
        executor(method, "http://test.com")

    # Must fail fast: only one attempt, no retries
    assert mock_send.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["POST", "PATCH"])
async def test_non_idempotent_method_does_not_retry_on_connect_error_async(method: str):
    """Non-idempotent methods must not retry on network errors (async)."""
    mock_send = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

    executor = AsyncRequestExecutor(send=mock_send, retries=3, backoff_factor=0.01)

    with pytest.raises(httpx.ConnectError):
        await executor(method, "http://test.com")

    # Must fail fast: only one attempt, no retries
    assert mock_send.call_count == 1
