import imednet.endpoints.records as records_module
from imednet.endpoints.jobs import JobsEndpoint
from imednet.endpoints.records import RecordsEndpoint


def test_records_endpoint_keeps_public_read_api(dummy_client, context, paginator_factory):
    endpoint = RecordsEndpoint(dummy_client, context)
    capture = paginator_factory(records_module, [{"recordId": 1}])

    listed = endpoint.list(study_key="S1")
    fetched = endpoint.get("S1", 1)

    assert callable(endpoint.list)
    assert callable(endpoint.get)
    assert listed[0].record_id == 1
    assert fetched.record_id == 1
    assert capture["path"] == "/api/v1/edc/studies/S1/records"


def test_jobs_endpoint_keeps_public_read_api(dummy_client, context, response_factory):
    endpoint = JobsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"jobId": "1"})

    result = endpoint.get("S1", "B1")

    assert callable(endpoint.list)
    assert callable(endpoint.get)
    assert result.job_id == "1"
    assert "ListEndpointMixin" not in {cls.__name__ for cls in JobsEndpoint.__mro__}
    assert "PathGetEndpointMixin" not in {cls.__name__ for cls in JobsEndpoint.__mro__}
