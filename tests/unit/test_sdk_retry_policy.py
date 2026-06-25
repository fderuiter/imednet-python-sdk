"""Unit tests for sdk retry policy."""

import httpx
import pytest
import respx

from imednet import errors
from imednet.core.retry import RetryPolicy, RetryState
from imednet.sdk import AsyncImednetSDK, ImednetSDK


class NamedPolicy(RetryPolicy):
    """Test suite for NamedPolicy."""

    def __init__(self, name: str) -> None:
        """Initialize the test object."""
        self.name = name

    def should_retry(self, state: RetryState) -> bool:  # pragma: no cover - simple
        """Helper function to should retry."""
        return False


@pytest.fixture()
def async_sdk() -> AsyncImednetSDK:
    """Helper function to async sdk."""
    return AsyncImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )


@pytest.fixture
def respx_mock_external():
    """Helper function to respx mock external."""
    with respx.mock(base_url="https://example.com") as mock:
        yield mock


def test_initial_retry_policy_propagates_to_async_client() -> None:
    """Test that initial retry policy propagates to async client."""
    policy = NamedPolicy("init")
    sdk = AsyncImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
        retry_policy=policy,
    )

    assert sdk._async_client.retry_policy is policy


def test_retry_policy_propagates_to_async_client(async_sdk: AsyncImednetSDK) -> None:
    """Test that retry policy propagates to async client."""
    async_policy = NamedPolicy("async")
    async_sdk._async_client.retry_policy = async_policy

    new_policy = NamedPolicy("new")
    async_sdk.retry_policy = new_policy

    assert async_sdk._async_client.retry_policy is new_policy


def test_default_retry_policy_retries_connection_error(respx_mock_external) -> None:
    """Verify that connection errors trigger retries."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    # Simulate a persistent connection error
    route = respx_mock_external.get("/test").mock(
        side_effect=httpx.ConnectError("Network Error", request=None)
    )

    # Note: RequestExecutor configures tenacity with reraise=False, so the underlying
    # httpx.ConnectError is wrapped in errors.RequestError.
    with pytest.raises(errors.RequestError) as exc_info:
        sdk._client.get("/test")

    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)

    # Should attempt 3 times (default retries=3)
    assert route.call_count == 3


def test_default_retry_policy_retries_on_500(respx_mock_external) -> None:
    """Verify that server errors (500) trigger retries."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    route = respx_mock_external.get("/test").mock(return_value=httpx.Response(500))

    with pytest.raises(errors.ServerError):
        sdk._client.get("/test")

    # Should attempt 3 times
    assert route.call_count == 3


def test_default_retry_policy_retries_on_429(respx_mock_external) -> None:
    """Verify that rate limit errors (429) trigger retries."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    route = respx_mock_external.get("/test").mock(return_value=httpx.Response(429))

    with pytest.raises(errors.RateLimitError):
        sdk._client.get("/test")

    # Should attempt 3 times
    assert route.call_count == 3


@pytest.mark.asyncio
async def test_default_retry_policy_async_retries_on_500(respx_mock_external) -> None:
    """Verify that server errors (500) trigger retries in async client."""
    sdk = AsyncImednetSDK(
        api_key="k",
        security_key="s",
        base_url="https://example.com",
        retries=3,
    )

    route = respx_mock_external.get("/test").mock(return_value=httpx.Response(500))

    with pytest.raises(errors.ServerError):
        await sdk._async_client.get("/test")

    # Should attempt 3 times
    assert route.call_count == 3


def test_default_retry_policy_post_does_not_retry_on_server_error(respx_mock_external) -> None:
    """Verify that POST requests receiving 5xx do NOT retry (non-idempotent)."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    route = respx_mock_external.post("/test").mock(return_value=httpx.Response(503))

    with pytest.raises(errors.ServerError):
        sdk._client.post("/test", json={})

    # Must fail fast: only one attempt, no retries
    assert route.call_count == 1


def test_default_retry_policy_post_retries_on_rate_limit(respx_mock_external) -> None:
    """Verify that POST requests receiving 429 DO retry (server rejected before processing)."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    route = respx_mock_external.post("/test").mock(return_value=httpx.Response(429))

    with pytest.raises(errors.RateLimitError):
        sdk._client.post("/test", json={})

    # Should attempt 3 times (rate limit is safe to retry for any method)
    assert route.call_count == 3
