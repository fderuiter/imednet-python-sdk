import imednet.sdk as sdk_mod
from imednet.core.client import Client
from imednet.core.context import Context
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
from imednet.workflows.data_extraction import DataExtractionWorkflow
from imednet.workflows.query_management import QueryManagementWorkflow
from imednet.workflows.record_mapper import RecordMapper
from imednet.workflows.record_update import RecordUpdateWorkflow
from imednet.workflows.subject_data import SubjectDataWorkflow


def _create_sdk() -> sdk_mod.ImednetSDK:
    return sdk_mod.ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )


def test_env_var_credentials(monkeypatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "env_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_secret")

    sdk = sdk_mod.ImednetSDK()

    assert isinstance(sdk._client, Client)


def test_sdk_initialization_wires_endpoints_and_workflows() -> None:
    sdk = _create_sdk()

    assert isinstance(sdk.ctx, Context)
    assert isinstance(sdk._client, Client)

    endpoints = {
        "codings": CodingsEndpoint,
        "forms": FormsEndpoint,
        "intervals": IntervalsEndpoint,
        "jobs": JobsEndpoint,
        "queries": QueriesEndpoint,
        "record_revisions": RecordRevisionsEndpoint,
        "records": RecordsEndpoint,
        "sites": SitesEndpoint,
        "studies": StudiesEndpoint,
        "subjects": SubjectsEndpoint,
        "users": UsersEndpoint,
        "variables": VariablesEndpoint,
        "visits": VisitsEndpoint,
    }
    for name, cls in endpoints.items():
        assert isinstance(getattr(sdk, name), cls)

    assert isinstance(sdk.workflows, sdk_mod.Workflows)
    assert isinstance(sdk.workflows.data_extraction, DataExtractionWorkflow)
    assert isinstance(sdk.workflows.query_management, QueryManagementWorkflow)
    assert isinstance(sdk.workflows.record_mapper, RecordMapper)
    assert isinstance(sdk.workflows.record_update, RecordUpdateWorkflow)
    assert isinstance(sdk.workflows.subject_data, SubjectDataWorkflow)


def test_context_management_closes_client(monkeypatch) -> None:
    called = {"close": False}

    def fake_close(self) -> None:
        called["close"] = True

    monkeypatch.setattr(Client, "close", fake_close)

    with _create_sdk() as sdk:
        assert isinstance(sdk, sdk_mod.ImednetSDK)

    assert called["close"]
