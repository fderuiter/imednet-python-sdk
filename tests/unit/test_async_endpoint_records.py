from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_records import AsyncRecordsEndpoint


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    return AsyncRecordsEndpoint(client, ctx)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_records.AsyncPaginator")
@patch("imednet.endpoints.async_records.Record")
@patch("imednet.endpoints.async_records.build_filter_string")
async def test_list(mock_build, mock_record, mock_pag, endpoint):
    mock_build.return_value = "a=b"
    mock_pag.return_value.__aiter__.return_value = [{"id": 1}]
    mock_record.from_json.side_effect = lambda x: x

    result = await endpoint.list(study_key="S1", a="b")
    assert result == [{"id": 1}]
    assert mock_build.called
    assert mock_pag.called


@pytest.mark.asyncio
@patch("imednet.endpoints.async_records.Record")
async def test_get(mock_record, endpoint):
    mock_record.from_json.return_value = {"id": 4}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"data": [{"id": 4}]}))
    result = await endpoint.get("S1", 4)
    assert result == {"id": 4}


@pytest.mark.asyncio
@patch("imednet.endpoints.async_records.Job")
async def test_create(mock_job, endpoint):
    mock_job.from_json.return_value = {"batch": "1"}
    endpoint._client.post = AsyncMock(return_value=MagicMock(json=lambda: {"batch": "1"}))
    result = await endpoint.create("S1", [{"foo": "bar"}])
    assert result == {"batch": "1"}
