import pytest
from unittest.mock import AsyncMock, MagicMock

import imednet.endpoints.jobs as jobs
from imednet.models.jobs import Job, JobStatus


@pytest.fixture
def dummy_client_async():
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


def test_get_success(dummy_client, context, response_factory):
    ep = jobs.JobsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"jobId": "1"})

    result = ep.get("S1", "B1")

    dummy_client.get.assert_called_once_with("/api/v1/edc/studies/S1/jobs/B1")
    assert isinstance(result, JobStatus)


def test_get_not_found(dummy_client, context, response_factory):
    ep = jobs.JobsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({})
    with pytest.raises(ValueError):
        ep.get("S1", "B1")


def test_list_success(dummy_client, context, response_factory):
    ep = jobs.JobsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory([
        {"jobId": "1", "batchId": "B1", "state": "COMPLETED"},
        {"jobId": "2", "batchId": "B2", "state": "PROCESSING"}
    ])

    result = ep.list("S1")

    dummy_client.get.assert_called_with("/api/v1/edc/studies/S1/jobs", params={})

    assert len(result) == 2
    assert isinstance(result[0], Job)
    assert result[0].job_id == "1"
    assert result[1].job_id == "2"


@pytest.mark.asyncio
async def test_async_list_success(dummy_client_async, context, response_factory):
    ep = jobs.JobsEndpoint(dummy_client_async, context, async_client=dummy_client_async)
    dummy_client_async.get.return_value = response_factory([
        {"jobId": "1", "batchId": "B1", "state": "COMPLETED"}
    ])

    result = await ep.async_list("S1")

    dummy_client_async.get.assert_called_with("/api/v1/edc/studies/S1/jobs", params={})
    assert len(result) == 1
    assert isinstance(result[0], Job)
    assert result[0].job_id == "1"
