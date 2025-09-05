import pytest

import imednet.api.endpoints.jobs as jobs
from imednet.api.models.jobs import JobStatus


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
