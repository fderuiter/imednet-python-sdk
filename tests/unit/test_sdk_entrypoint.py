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
import imednet.sdk as sdk_mod
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


def test_convenience_methods_delegate_to_endpoints(monkeypatch) -> None:
    sdk = _create_sdk()
    calls = {}

    def fake_studies_list(**kw):
        calls["studies"] = kw
        return ["STUDY"]

    def fake_records_list(study_key, record_data_filter=None, **kw):
        calls["records"] = (study_key, record_data_filter, kw)
        return ["REC"]

    def fake_sites_list(study_key, **kw):
        calls["sites"] = (study_key, kw)
        return ["SITE"]

    def fake_subjects_list(study_key, **kw):
        calls["subjects"] = (study_key, kw)
        return ["SUB"]

    def fake_create(study_key, records_data, email_notify=None):
        calls["create"] = (study_key, records_data, email_notify)
        return "JOB"

    def fake_forms_list(study_key, **kw):
        calls["forms"] = (study_key, kw)
        return ["FORM"]

    def fake_intervals_list(study_key, **kw):
        calls["intervals"] = (study_key, kw)
        return ["INT"]

    def fake_variables_list(study_key, **kw):
        calls["variables"] = (study_key, kw)
        return ["VAR"]

    def fake_visits_list(study_key, **kw):
        calls["visits"] = (study_key, kw)
        return ["VIS"]

    def fake_codings_list(study_key, **kw):
        calls["codings"] = (study_key, kw)
        return ["COD"]

    def fake_queries_list(study_key, **kw):
        calls["queries"] = (study_key, kw)
        return ["QUERY"]

    def fake_record_revisions_list(study_key, **kw):
        calls["record_revisions"] = (study_key, kw)
        return ["REV"]

    def fake_users_list(study_key, include_inactive=False):
        calls["users"] = (study_key, include_inactive)
        return ["USER"]

    def fake_get_job(study_key, batch_id):
        calls["job"] = (study_key, batch_id)
        return "JOBOBJ"

    monkeypatch.setattr(sdk.studies, "list", fake_studies_list)
    monkeypatch.setattr(sdk.records, "list", fake_records_list)
    monkeypatch.setattr(sdk.sites, "list", fake_sites_list)
    monkeypatch.setattr(sdk.subjects, "list", fake_subjects_list)
    monkeypatch.setattr(sdk.records, "create", fake_create)
    monkeypatch.setattr(sdk.forms, "list", fake_forms_list)
    monkeypatch.setattr(sdk.intervals, "list", fake_intervals_list)
    monkeypatch.setattr(sdk.variables, "list", fake_variables_list)
    monkeypatch.setattr(sdk.visits, "list", fake_visits_list)
    monkeypatch.setattr(sdk.codings, "list", fake_codings_list)
    monkeypatch.setattr(sdk.queries, "list", fake_queries_list)
    monkeypatch.setattr(sdk.record_revisions, "list", fake_record_revisions_list)
    monkeypatch.setattr(sdk.users, "list", fake_users_list)
    monkeypatch.setattr(sdk.jobs, "get", fake_get_job)

    assert sdk.get_studies(status="active") == ["STUDY"]
    assert sdk.get_records("S1", record_data_filter="x") == ["REC"]
    assert sdk.get_sites("S1", country="US") == ["SITE"]
    assert sdk.get_subjects("S1", status="new") == ["SUB"]
    assert sdk.create_record("S1", [{"a": 1}], email_notify=True) == "JOB"
    assert sdk.get_forms("S1", page=2) == ["FORM"]
    assert sdk.get_intervals("S1") == ["INT"]
    assert sdk.get_variables("S1") == ["VAR"]
    assert sdk.get_visits("S1") == ["VIS"]
    assert sdk.get_codings("S1") == ["COD"]
    assert sdk.get_queries("S1", status="open") == ["QUERY"]
    assert sdk.get_record_revisions("S1") == ["REV"]
    assert sdk.get_users("S1", include_inactive=True) == ["USER"]
    assert sdk.get_job("S1", "B1") == "JOBOBJ"

    assert calls["studies"] == {"status": "active"}
    assert calls["records"] == ("S1", "x", {})
    assert calls["sites"] == ("S1", {"country": "US"})
    assert calls["subjects"] == ("S1", {"status": "new"})
    assert calls["create"] == ("S1", [{"a": 1}], True)
    assert calls["forms"] == ("S1", {"page": 2})
    assert calls["intervals"] == ("S1", {})
    assert calls["variables"] == ("S1", {})
    assert calls["visits"] == ("S1", {})
    assert calls["codings"] == ("S1", {})
    assert calls["queries"] == ("S1", {"status": "open"})
    assert calls["record_revisions"] == ("S1", {})
    assert calls["users"] == ("S1", True)
    assert calls["job"] == ("S1", "B1")
