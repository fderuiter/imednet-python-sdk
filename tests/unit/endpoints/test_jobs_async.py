import pytest
from unittest.mock import AsyncMock, Mock

import imednet.endpoints.jobs as jobs
from imednet.models.jobs import JobStatus


@pytest.mark.asyncio
async def test_async_get_success(dummy_client, context, response_factory):
    # Setup async mock
    async_client = AsyncMock()
    async_client.get.return_value = response_factory({"jobId": "1"})

    ep = jobs.JobsEndpoint(dummy_client, context, async_client=async_client)

    result = await ep.async_get("S1", "B1")

    async_client.get.assert_called_once_with("/api/v1/edc/studies/S1/jobs/B1")
    assert isinstance(result, JobStatus)

@pytest.mark.asyncio
async def test_async_get_not_found(dummy_client, context, response_factory):
    async_client = AsyncMock()
    async_client.get.return_value = response_factory({})

    ep = jobs.JobsEndpoint(dummy_client, context, async_client=async_client)

    with pytest.raises(ValueError):
        await ep.async_get("S1", "B1")
