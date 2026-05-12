import imednet.endpoints.records as records_module
from imednet.endpoints.codings import CodingsEndpoint
from imednet.endpoints.forms import FormsEndpoint
from imednet.endpoints.intervals import IntervalsEndpoint
from imednet.endpoints.jobs import JobsEndpoint
from imednet.endpoints.queries import QueriesEndpoint
from imednet.endpoints.record_revisions import RecordRevisionsEndpoint
from imednet.endpoints.records import RecordsEndpoint
from imednet.endpoints.sites import SitesEndpoint
from imednet.endpoints.studies import StudiesEndpoint
from imednet.endpoints.subjects import SubjectsEndpoint
from imednet.endpoints.users import UsersEndpoint
from imednet.endpoints.variables import VariablesEndpoint
from imednet.endpoints.visits import VisitsEndpoint

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


def test_all_endpoints_inherit_from_single_edc_base():
    """Endpoints must have EdcGenericListGetEndpoint as their sole direct parent."""
    for endpoint_cls in ALL_ENDPOINT_CLASSES:
        direct_bases = endpoint_cls.__bases__
        base_names = {b.__name__ for b in direct_bases}
        assert base_names == {
            "EdcGenericListGetEndpoint"
        }, f"{endpoint_cls.__name__} has unexpected direct bases: {base_names}"


def test_no_endpoint_directly_inherits_edc_mixin():
    """EdcEndpointMixin must not appear as a direct base of any concrete endpoint."""
    for endpoint_cls in ALL_ENDPOINT_CLASSES:
        direct_base_names = {b.__name__ for b in endpoint_cls.__bases__}
        assert (
            "EdcEndpointMixin" not in direct_base_names
        ), f"{endpoint_cls.__name__} still directly inherits EdcEndpointMixin"
