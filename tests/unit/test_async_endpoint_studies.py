from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_studies import AsyncStudiesEndpoint


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    return AsyncStudiesEndpoint(client, ctx, 200)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_studies.AsyncPaginator")
@patch("imednet.endpoints.async_studies.Study")
@patch("imednet.endpoints.async_studies.build_filter_string")
async def test_list_with_filters(mock_build, mock_study, mock_pag, endpoint):
    mock_build.return_value = "foo=bar"
    mock_pag.return_value.__aiter__.return_value = [{"id": 1}]
    mock_study.model_validate.side_effect = lambda x: x

    result = await endpoint.list(foo="bar")
    assert mock_build.called
    assert mock_pag.called
    assert result == [{"id": 1}]
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 200


@pytest.mark.asyncio
@patch("imednet.endpoints.async_studies.AsyncPaginator")
@patch("imednet.endpoints.async_studies.Study")
async def test_list_no_filters(mock_study, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = [{"id": 2}]
    mock_study.model_validate.side_effect = lambda x: x

    result = await endpoint.list()
    assert result == [{"id": 2}]
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 200


@pytest.mark.asyncio
@patch("imednet.endpoints.async_studies.AsyncPaginator")
@patch("imednet.endpoints.async_studies.Study")
async def test_custom_page_size(mock_study, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = []
    mock_study.model_validate.side_effect = lambda x: x

    await endpoint.list(page_size=80)
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 80


@pytest.mark.asyncio
@patch("imednet.endpoints.async_studies.Study")
async def test_get_returns_study(mock_study, endpoint):
    mock_study.model_validate.return_value = {"id": "S1"}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": "S1"}]}))
    result = await endpoint.get("S1")
    assert result == {"id": "S1"}


@pytest.mark.asyncio
async def test_get_raises(endpoint):
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": []}))
    with pytest.raises(ValueError):
        await endpoint.get("S2")
