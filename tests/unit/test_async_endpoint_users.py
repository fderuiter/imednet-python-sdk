from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_users import AsyncUsersEndpoint
from imednet.endpoints.helpers import build_paginator


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    ctx.default_study_key = "DEF"
    return AsyncUsersEndpoint(client, ctx)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_users.AsyncPaginator")
@patch("imednet.endpoints.async_users.User")
@patch("imednet.endpoints.async_users.build_paginator", wraps=build_paginator)
async def test_list(mock_builder, mock_user, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = [{"id": "u"}]
    mock_user.from_json.side_effect = lambda x: x

    result = await endpoint.list("S1", include_inactive=True)
    assert result == [{"id": "u"}]
    mock_builder.assert_called_once()
    assert mock_pag.called


@pytest.mark.asyncio
@patch("imednet.endpoints.async_users.User")
async def test_get(mock_user, endpoint):
    mock_user.from_json.return_value = {"id": "u"}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": "u"}]}))

    result = await endpoint.get("S1", "u")
    assert result == {"id": "u"}


@pytest.mark.asyncio
async def test_list_missing_study_key(endpoint):
    endpoint._ctx.default_study_key = None
    with pytest.raises(ValueError):
        await endpoint.list()
