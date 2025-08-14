import pytest

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
