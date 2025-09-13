import pytest

from imednet.api.core.async_client import AsyncClient
from imednet.api.core.client import Client


def test_client_strips_api_suffix() -> None:
    client = Client(api_key="k", security_key="s", base_url="https://x/api")
    assert client.base_url == "https://x"


@pytest.mark.asyncio
async def test_async_client_strips_api_suffix() -> None:
    async with AsyncClient(
        api_key="k",
        security_key="s",
        base_url="https://x/api",
    ) as client:
        assert client.base_url == "https://x"
