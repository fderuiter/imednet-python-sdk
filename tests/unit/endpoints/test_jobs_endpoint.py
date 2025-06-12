import imednet.endpoints.jobs as jobs
import pytest
from imednet.models.jobs import Job


def test_get_success(dummy_client, context, response_factory):
    ep = jobs.JobsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"jobId": "1"})

    result = ep.get("S1", "B1")

    dummy_client.get.assert_called_once_with("/api/v1/edc/studies/S1/jobs/B1")
    assert isinstance(result, Job)


def test_get_not_found(dummy_client, context, response_factory):
    ep = jobs.JobsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({})
    with pytest.raises(ValueError):
        ep.get("S1", "B1")
