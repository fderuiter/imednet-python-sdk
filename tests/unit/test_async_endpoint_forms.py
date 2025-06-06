from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_forms import AsyncFormsEndpoint


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    return AsyncFormsEndpoint(client, ctx, 200)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_forms.AsyncPaginator")
@patch("imednet.endpoints.async_forms.Form")
@patch("imednet.endpoints.async_forms.build_filter_string")
async def test_list(mock_build, mock_form, mock_pag, endpoint):
    mock_build.return_value = "foo=bar"
    mock_pag.return_value.__aiter__.return_value = [{"id": 1}]
    mock_form.from_json.side_effect = lambda x: x

    result = await endpoint.list(study_key="S1", foo="bar")
    assert result == [{"id": 1}]
    assert mock_build.called
    assert mock_pag.called
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 200


@pytest.mark.asyncio
@patch("imednet.endpoints.async_forms.AsyncPaginator")
@patch("imednet.endpoints.async_forms.Form")
async def test_custom_page_size(mock_form, mock_pag, endpoint):
    mock_pag.return_value.__aiter__.return_value = []
    mock_form.from_json.side_effect = lambda x: x

    await endpoint.list(page_size=70)
    args, kwargs = mock_pag.call_args
    assert kwargs["page_size"] == 70


@pytest.mark.asyncio
@patch("imednet.endpoints.async_forms.Form")
async def test_get(mock_form, endpoint):
    mock_form.from_json.return_value = {"id": 123}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": 123}]}))
    result = await endpoint.get("S1", 123)
    assert result == {"id": 123}
