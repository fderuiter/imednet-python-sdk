from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_codings import AsyncCodingsEndpoint


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    ctx.default_study_key = "DEF"
    return AsyncCodingsEndpoint(client, ctx)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_codings.AsyncPaginator")
@patch("imednet.endpoints.async_codings.Coding")
@patch("imednet.endpoints.async_codings.build_paginator")
async def test_list(mock_builder, mock_model, mock_pag, endpoint):
    mock_builder.return_value = mock_pag.return_value
    mock_pag.return_value.__aiter__.return_value = [{"id": 1}]
    mock_model.from_json.side_effect = lambda x: x

    result = await endpoint.list(study_key="S1", x="y")
    assert result == [{"id": 1}]
    mock_builder.assert_called_once()


@pytest.mark.asyncio
@patch("imednet.endpoints.async_codings.Coding")
async def test_get(mock_model, endpoint):
    mock_model.from_json.return_value = {"id": 2}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": 2}]}))

    result = await endpoint.get("S1", "2")
    assert result == {"id": 2}


@pytest.mark.asyncio
async def test_list_no_study_key(endpoint):
    endpoint._ctx.default_study_key = None
    with pytest.raises(ValueError):
        await endpoint.list()
