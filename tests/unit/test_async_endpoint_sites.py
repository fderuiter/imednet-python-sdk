from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_sites import AsyncSitesEndpoint


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    return AsyncSitesEndpoint(client, ctx)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_sites.AsyncPaginator")
@patch("imednet.endpoints.async_sites.Site")
@patch("imednet.endpoints.async_sites.build_filter_string")
async def test_list(mock_build, mock_site, mock_pag, endpoint):
    mock_build.return_value = "f=b"
    mock_pag.return_value.__aiter__.return_value = [{"id": 1}]
    mock_site.from_json.side_effect = lambda x: x

    result = await endpoint.list(study_key="S1", f="b")
    assert result == [{"id": 1}]
    assert mock_build.called
    assert mock_pag.called


@pytest.mark.asyncio
@patch("imednet.endpoints.async_sites.Site")
async def test_get(mock_site, endpoint):
    mock_site.from_json.return_value = {"id": 2}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": 2}]}))
    result = await endpoint.get("S1", 2)
    assert result == {"id": 2}
