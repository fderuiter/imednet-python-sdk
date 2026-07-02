"""Unit tests for endpoint composition."""

import imednet.endpoints.records as records_module
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncCodingsEndpoint = ASYNC_ENDPOINT_REGISTRY['codings']
CodingsEndpoint = ENDPOINT_REGISTRY['codings']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncFormsEndpoint = ASYNC_ENDPOINT_REGISTRY['forms']
FormsEndpoint = ENDPOINT_REGISTRY['forms']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncIntervalsEndpoint = ASYNC_ENDPOINT_REGISTRY['intervals']
IntervalsEndpoint = ENDPOINT_REGISTRY['intervals']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncJobsEndpoint = ASYNC_ENDPOINT_REGISTRY['jobs']
JobsEndpoint = ENDPOINT_REGISTRY['jobs']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncQueriesEndpoint = ASYNC_ENDPOINT_REGISTRY['queries']
QueriesEndpoint = ENDPOINT_REGISTRY['queries']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncRecordRevisionsEndpoint = ASYNC_ENDPOINT_REGISTRY['record_revisions']
RecordRevisionsEndpoint = ENDPOINT_REGISTRY['record_revisions']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncRecordsEndpoint = ASYNC_ENDPOINT_REGISTRY['records']
RecordsEndpoint = ENDPOINT_REGISTRY['records']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncSitesEndpoint = ASYNC_ENDPOINT_REGISTRY['sites']
SitesEndpoint = ENDPOINT_REGISTRY['sites']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncStudiesEndpoint = ASYNC_ENDPOINT_REGISTRY['studies']
StudiesEndpoint = ENDPOINT_REGISTRY['studies']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncSubjectsEndpoint = ASYNC_ENDPOINT_REGISTRY['subjects']
SubjectsEndpoint = ENDPOINT_REGISTRY['subjects']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncUsersEndpoint = ASYNC_ENDPOINT_REGISTRY['users']
UsersEndpoint = ENDPOINT_REGISTRY['users']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncVariablesEndpoint = ASYNC_ENDPOINT_REGISTRY['variables']
VariablesEndpoint = ENDPOINT_REGISTRY['variables']
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
AsyncVisitsEndpoint = ASYNC_ENDPOINT_REGISTRY['visits']
VisitsEndpoint = ENDPOINT_REGISTRY['visits']

ALL_ENDPOINT_CLASSES = [
    CodingsEndpoint,
    FormsEndpoint,
    IntervalsEndpoint,
    JobsEndpoint,
    QueriesEndpoint,
    RecordRevisionsEndpoint,
    RecordsEndpoint,
    SitesEndpoint,
    StudiesEndpoint,
    SubjectsEndpoint,
    UsersEndpoint,
    VariablesEndpoint,
    VisitsEndpoint,
]

ALL_ASYNC_ENDPOINT_CLASSES = [
    AsyncCodingsEndpoint,
    AsyncFormsEndpoint,
    AsyncIntervalsEndpoint,
    AsyncJobsEndpoint,
    AsyncQueriesEndpoint,
    AsyncRecordRevisionsEndpoint,
    AsyncRecordsEndpoint,
    AsyncSitesEndpoint,
    AsyncStudiesEndpoint,
    AsyncSubjectsEndpoint,
    AsyncUsersEndpoint,
    AsyncVariablesEndpoint,
    AsyncVisitsEndpoint,
]


def test_records_endpoint_keeps_public_read_api(dummy_client, context, paginator_factory):
    """Test that records endpoint keeps public read api."""
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
    """Test that jobs endpoint keeps public read api."""
    endpoint = JobsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"jobId": "1"})

    result = endpoint.get("S1", "B1")

    assert callable(endpoint.list)
    assert callable(endpoint.get)
    assert result.job_id == "1"
    assert "ListEndpointMixin" not in {cls.__name__ for cls in JobsEndpoint.__mro__}
    assert "PathGetEndpointMixin" not in {cls.__name__ for cls in JobsEndpoint.__mro__}


def test_all_endpoints_inherit_from_single_edc_base():
    """Endpoints must have EdcSyncListGetEndpoint as their sole direct parent."""
    for endpoint_cls in ALL_ENDPOINT_CLASSES:
        direct_bases = endpoint_cls.__bases__
        base_names = {b.__name__ for b in direct_bases if not b.__name__.endswith("OperationDef") and not b.__name__.endswith("Mixin")}
        assert base_names == {"EdcSyncListGetEndpoint"}, (
            f"{endpoint_cls.__name__} has unexpected direct bases: {base_names}"
        )


def test_no_endpoint_directly_inherits_edc_mixin():
    """EdcEndpointMixin must not appear as a direct base of any concrete endpoint."""
    for endpoint_cls in ALL_ENDPOINT_CLASSES:
        direct_base_names = {b.__name__ for b in endpoint_cls.__bases__ if not b.__name__.endswith("OperationDef") and not b.__name__.endswith("Mixin")}
        assert "EdcEndpointMixin" not in direct_base_names, (
            f"{endpoint_cls.__name__} still directly inherits EdcEndpointMixin"
        )


def test_all_async_endpoints_inherit_from_single_edc_base():
    """Async endpoints must have EdcAsyncListGetEndpoint as their sole direct parent."""
    for endpoint_cls in ALL_ASYNC_ENDPOINT_CLASSES:
        base_names = {b.__name__ for b in endpoint_cls.__bases__ if not b.__name__.endswith("OperationDef") and not b.__name__.endswith("Mixin")}
        assert base_names == {"EdcAsyncListGetEndpoint"}, (
            f"{endpoint_cls.__name__} has unexpected direct bases: {base_names}"
        )
