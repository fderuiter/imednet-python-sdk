import asyncio
from unittest.mock import AsyncMock

import pytest

import imednet.endpoints.jobs as jobs
from imednet.models.jobs import JobStatus


@pytest.mark.parametrize("use_async", [False, True])
def test_get_success(dummy_client, context, response_factory, use_async):
    ep = jobs.JobsEndpoint(dummy_client, context, async_client=dummy_client if use_async else None)
    if use_async:
        dummy_client.get = AsyncMock(return_value=response_factory({"jobId": "1"}))
    else:
        dummy_client.get.return_value = response_factory({"jobId": "1"})

    if use_async:
        result = asyncio.run(ep.async_get("S1", "B1"))
    else:
        result = ep.get("S1", "B1")

    if use_async:
        dummy_client.get.assert_awaited_once_with("/api/v1/edc/studies/S1/jobs/B1")
    else:
        dummy_client.get.assert_called_once_with("/api/v1/edc/studies/S1/jobs/B1")
    assert isinstance(result, JobStatus)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(dummy_client, context, response_factory, use_async):
    ep = jobs.JobsEndpoint(dummy_client, context, async_client=dummy_client if use_async else None)
    if use_async:
        dummy_client.get = AsyncMock(return_value=response_factory({}))
    else:
        dummy_client.get.return_value = response_factory({})
    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", "B1"))
        else:
            ep.get("S1", "B1")
