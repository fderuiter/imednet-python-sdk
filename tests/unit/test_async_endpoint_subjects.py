from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_subjects import AsyncSubjectsEndpoint


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    return AsyncSubjectsEndpoint(client, ctx, 200)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_subjects.AsyncPaginator")
@patch("imednet.endpoints.async_subjects.Subject")
@patch("imednet.endpoints.async_subjects.build_filter_string")
async def test_list(mock_build, mock_subject, mock_pag, endpoint):
    mock_build.return_value = "x=y"
    mock_pag.return_value.__aiter__.return_value = [{"id": "s"}]
    mock_subject.from_json.side_effect = lambda x: x

    result = await endpoint.list(study_key="S1", x="y")
    assert result == [{"id": "s"}]
    assert mock_build.called
    assert mock_pag.called
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 200


@pytest.mark.asyncio
@patch("imednet.endpoints.async_subjects.AsyncPaginator")
@patch("imednet.endpoints.async_subjects.Subject")
async def test_custom_page_size(mock_subject, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = []
    mock_subject.from_json.side_effect = lambda x: x

    await endpoint.list(page_size=65)
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 65


@pytest.mark.asyncio
@patch("imednet.endpoints.async_subjects.Subject")
async def test_get(mock_subject, endpoint):
    mock_subject.from_json.return_value = {"id": "S"}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": "S"}]}))
    result = await endpoint.get("S1", "S")
    assert result == {"id": "S"}
