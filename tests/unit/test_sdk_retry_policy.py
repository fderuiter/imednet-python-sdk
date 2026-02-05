import httpx
import pytest
import respx

from imednet.core import exceptions
from imednet.core.retry import RetryPolicy, RetryState
from imednet.sdk import ImednetSDK


class NamedPolicy(RetryPolicy):
    def __init__(self, name: str) -> None:
        self.name = name

    def should_retry(self, state: RetryState) -> bool:  # pragma: no cover - simple
        return False


@pytest.fixture()
def sdk() -> ImednetSDK:
    return ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
        enable_async=True,
    )


@pytest.fixture
def respx_mock_external():
    with respx.mock(base_url="https://example.com") as mock:
        yield mock


def test_initial_retry_policy_propagates_to_clients() -> None:
    policy = NamedPolicy("init")
    sdk = ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
        enable_async=True,
        retry_policy=policy,
    )

    assert sdk._client.retry_policy is policy
    assert sdk._async_client is not None
    assert sdk._async_client.retry_policy is policy


def test_retry_policy_propagates_to_clients(sdk: ImednetSDK) -> None:
    assert sdk._async_client is not None

    client_policy = NamedPolicy("client")
    async_policy = NamedPolicy("async")
    sdk._client.retry_policy = client_policy
    sdk._async_client.retry_policy = async_policy

    new_policy = NamedPolicy("new")
    sdk.retry_policy = new_policy

    assert sdk._client.retry_policy is new_policy
    assert sdk._async_client.retry_policy is new_policy


def test_default_retry_policy_retries_connection_error(respx_mock_external) -> None:
    """Verify that connection errors trigger retries."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    # Simulate a persistent connection error
    route = respx_mock_external.get("/test").mock(
        side_effect=httpx.ConnectError("Network Error", request=None)
    )

    # Note: RequestExecutor configures tenacity with reraise=True, so the underlying
    # httpx.ConnectError bubbles up instead of being wrapped in exceptions.RequestError.
    with pytest.raises(httpx.ConnectError):
        sdk._client.get("/test")

    # Should attempt 3 times (default retries=3)
    assert route.call_count == 3


def test_default_retry_policy_no_retry_on_500(respx_mock_external) -> None:
    """Verify that server errors (500) do NOT trigger retries."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    route = respx_mock_external.get("/test").mock(return_value=httpx.Response(500))

    with pytest.raises(exceptions.ServerError):
        sdk._client.get("/test")

    # Should call only once
    assert route.call_count == 1


def test_default_retry_policy_no_retry_on_429(respx_mock_external) -> None:
    """Verify that rate limit errors (429) do NOT trigger retries."""
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://example.com", retries=3)
    route = respx_mock_external.get("/test").mock(return_value=httpx.Response(429))

    with pytest.raises(exceptions.RateLimitError):
        sdk._client.get("/test")

    # Should call only once
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_default_retry_policy_async_no_retry_on_500(respx_mock_external) -> None:
    """Verify that server errors (500) do NOT trigger retries in async client."""
    sdk = ImednetSDK(
        api_key="k",
        security_key="s",
        base_url="https://example.com",
        enable_async=True,
        retries=3,
    )
    assert sdk._async_client is not None

    route = respx_mock_external.get("/test").mock(return_value=httpx.Response(500))

    with pytest.raises(exceptions.ServerError):
        await sdk._async_client.get("/test")

    # Should call only once
    assert route.call_count == 1
