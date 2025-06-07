from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_variables import AsyncVariablesEndpoint
from imednet.endpoints.helpers import build_paginator


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    ctx.default_study_key = "DEF"
    return AsyncVariablesEndpoint(client, ctx)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_variables.AsyncPaginator")
@patch("imednet.endpoints.async_variables.Variable")
@patch("imednet.endpoints.async_variables.build_paginator", wraps=build_paginator)
async def test_list(mock_builder, mock_model, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = [{"id": 3}]
    mock_model.from_json.side_effect = lambda x: x

    result = await endpoint.list(study_key="S1", a="b")
    assert result == [{"id": 3}]
    mock_builder.assert_called_once()
    assert mock_pag.called


@pytest.mark.asyncio
@patch("imednet.endpoints.async_variables.Variable")
async def test_get(mock_model, endpoint):
    mock_model.from_json.return_value = {"id": 4}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": 4}]}))

    result = await endpoint.get("S1", 4)
    assert result == {"id": 4}
