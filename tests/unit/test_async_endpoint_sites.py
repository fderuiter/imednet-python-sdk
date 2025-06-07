from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_sites import AsyncSitesEndpoint
from imednet.endpoints.helpers import build_paginator


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    return AsyncSitesEndpoint(client, ctx, 200)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_sites.AsyncPaginator")
@patch("imednet.endpoints.async_sites.Site")
@patch("imednet.endpoints.async_sites.build_paginator", wraps=build_paginator)
async def test_list(mock_builder, mock_site, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = [{"id": 1}]
    mock_site.from_json.side_effect = lambda x: x

    result = await endpoint.list(study_key="S1", f="b")
    assert result == [{"id": 1}]
    mock_builder.assert_called_once()
    assert mock_pag.called
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 200


@pytest.mark.asyncio
@patch("imednet.endpoints.async_sites.AsyncPaginator")
@patch("imednet.endpoints.async_sites.Site")
async def test_custom_page_size(mock_site, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = []
    mock_site.from_json.side_effect = lambda x: x

    await endpoint.list(page_size=45)
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 45


@pytest.mark.asyncio
@patch("imednet.endpoints.async_sites.Site")
async def test_get(mock_site, endpoint):
    mock_site.from_json.return_value = {"id": 2}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": 2}]}))
    result = await endpoint.get("S1", 2)
    assert result == {"id": 2}
