from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.endpoints.async_jobs import AsyncJobsEndpoint


@pytest.fixture
def endpoint():
    client = MagicMock()
    ctx = MagicMock()
    return AsyncJobsEndpoint(client, ctx)


@pytest.mark.asyncio
@patch("imednet.endpoints.async_jobs.Job")
async def test_get(mock_job, endpoint):
    mock_job.from_json.return_value = {"batch": "1"}
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {"batch": "1"}))

    result = await endpoint.get("S1", "1")
    assert result == {"batch": "1"}


@pytest.mark.asyncio
async def test_get_not_found(endpoint):
    endpoint._client.get = AsyncMock(return_value=MagicMock(json=lambda: {}))
    with pytest.raises(ValueError):
        await endpoint.get("S1", "MISSING")
