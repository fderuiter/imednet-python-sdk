from unittest.mock import AsyncMock, patch

import pytest
from imednet.async_sdk import AsyncImednetSDK


@pytest.mark.asyncio
async def test_initialization():
    with patch("imednet.async_sdk.AsyncClient") as MockClient:
        client_instance = MockClient.return_value
        client_instance.aclose = AsyncMock()
        sdk = AsyncImednetSDK(api_key="k", security_key="s")
        assert sdk.studies
        MockClient.assert_called_once()
        await sdk.aclose()
        client_instance.aclose.assert_awaited_once()
