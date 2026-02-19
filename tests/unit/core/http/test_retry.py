from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from imednet.core.exceptions import RequestError
from imednet.core.http.executor import AsyncRequestExecutor, SyncRequestExecutor


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
