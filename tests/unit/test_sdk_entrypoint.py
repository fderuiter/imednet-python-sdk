"""TODO: Add docstring."""

from typing import Any, Callable

import pytest

import imednet.sdk as sdk_mod
from imednet.core.client import Client
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
from imednet.errors import PluginLoadError
from imednet.errors.orchestration import FilterConflictError, OrchestratorError
from imednet.orchestration import MultiStudyOrchestrator, OrchestratorResult, StudyWorkerCallable
from imednet_workflows.data_extraction import DataExtractionWorkflow
from imednet_workflows.query_management import QueryManagementWorkflow
from imednet_workflows.record_mapper import RecordMapper
from imednet_workflows.record_update import RecordUpdateWorkflow
from imednet_workflows.subject_data import SubjectDataWorkflow
from imednet_workflows.uat import StudySchemaInspector


class _FakeEntryPoint:
    """Minimal importlib.metadata.EntryPoint stand-in for plugin loader tests."""

    def __init__(
        self, loader: Callable[[], Any], value: str = "tests.fake_plugin:Workflows"
    ) -> None:
        """TODO: Add docstring."""
        self._loader = loader
        self.value = value

    def load(self):
        """TODO: Add docstring."""
        return self._loader()


def test_top_level_orchestration_exports() -> None:
    """TODO: Add docstring."""
    from imednet import FilterConflictError as TopLevelFilterConflictError
    from imednet import MultiStudyOrchestrator as TopLevelMultiStudyOrchestrator
    from imednet import OrchestratorError as TopLevelOrchestratorError
    from imednet import OrchestratorResult as TopLevelOrchestratorResult
    from imednet import StudyWorkerCallable as TopLevelStudyWorkerCallable

    assert TopLevelMultiStudyOrchestrator is MultiStudyOrchestrator
    assert TopLevelOrchestratorResult is OrchestratorResult
    assert TopLevelStudyWorkerCallable is StudyWorkerCallable
    assert TopLevelOrchestratorError is OrchestratorError
    assert TopLevelFilterConflictError is FilterConflictError


def test_sdk_workflows_uses_entry_point_discovery(monkeypatch) -> None:
    """TODO: Add docstring."""
    loaded = {"called": False}

    def load_workflows():
        """TODO: Add docstring."""
        loaded["called"] = True

        class FakeWorkflows:
            """TODO: Add docstring."""

            def __init__(self, sdk_instance):
                """TODO: Add docstring."""
                self.sdk_instance = sdk_instance

        return FakeWorkflows

    monkeypatch.setattr(
        sdk_mod,
        "entry_points",
        lambda *, group, name: (
            [_FakeEntryPoint(load_workflows)]
            if group == "imednet.plugins" and name == "workflows"
            else []
        ),
    )

    sdk = _create_sdk()

    assert loaded["called"]
    assert sdk.workflows.sdk_instance is sdk


@pytest.mark.parametrize("exception_class", [AttributeError, ImportError, ModuleNotFoundError])
def test_sdk_workflows_invalid_entry_point_load_raises_import_error(
    monkeypatch, exception_class
) -> None:
    """TODO: Add docstring."""

    def failing_loader():
        """TODO: Add docstring."""
        raise exception_class("boom")

    monkeypatch.setattr(
        sdk_mod,
        "entry_points",
        lambda *, group, name: (
            [_FakeEntryPoint(failing_loader)]
            if group == "imednet.plugins" and name == "workflows"
            else []
        ),
    )

    with pytest.raises(PluginLoadError, match="Failed to load workflows plugin from entry point"):
        _create_sdk()


def test_sdk_workflows_entry_point_must_be_callable(monkeypatch) -> None:
    """TODO: Add docstring."""
    monkeypatch.setattr(
        sdk_mod,
        "entry_points",
        lambda *, group, name: (
            [_FakeEntryPoint(lambda: object())]
            if group == "imednet.plugins" and name == "workflows"
            else []
        ),
    )

    with pytest.raises(PluginLoadError, match="must be a callable"):
        _create_sdk()


def test_sdk_workflows_multiple_plugins_raises_import_error(monkeypatch) -> None:
    """TODO: Add docstring."""
    monkeypatch.setattr(
        sdk_mod,
        "entry_points",
        lambda *, group, name: (
            [_FakeEntryPoint(lambda: object), _FakeEntryPoint(lambda: object)]
            if group == "imednet.plugins" and name == "workflows"
            else []
        ),
    )

    with pytest.raises(PluginLoadError, match="Multiple 'workflows' plugins were found"):
        _create_sdk()


def test_sdk_workflows_instantiation_failure_raises_import_error(monkeypatch) -> None:
    """TODO: Add docstring."""

    class BrokenWorkflows:
        """TODO: Add docstring."""

        def __init__(self, sdk_instance):
            """TODO: Add docstring."""
            raise TypeError("broken")

    monkeypatch.setattr(
        sdk_mod,
        "entry_points",
        lambda *, group, name: (
            [_FakeEntryPoint(lambda: BrokenWorkflows)]
            if group == "imednet.plugins" and name == "workflows"
            else []
        ),
    )

    with pytest.raises(PluginLoadError, match="Failed to instantiate workflows"):
        _create_sdk()


def _create_sdk() -> sdk_mod.ImednetSDK:
    """TODO: Add docstring."""
    return sdk_mod.ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )


def test_env_var_credentials(monkeypatch) -> None:
    """TODO: Add docstring."""
    monkeypatch.setenv("IMEDNET_API_KEY", "env_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_secret")

    sdk = sdk_mod.ImednetSDK()

    assert isinstance(sdk._client, Client)


def test_sdk_initialization_wires_endpoints_and_workflows() -> None:
    """TODO: Add docstring."""
    sdk = _create_sdk()

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

    assert isinstance(sdk.workflows.data_extraction, DataExtractionWorkflow)
    assert isinstance(sdk.workflows.query_management, QueryManagementWorkflow)
    assert isinstance(sdk.workflows.record_mapper, RecordMapper)
    assert isinstance(sdk.workflows.record_update, RecordUpdateWorkflow)
    assert isinstance(sdk.workflows.subject_data, SubjectDataWorkflow)
    assert isinstance(sdk.workflows.uat_inspector, StudySchemaInspector)


def test_context_management_closes_client(monkeypatch) -> None:
    """TODO: Add docstring."""
    called = {"close": False}

    def fake_close(self) -> None:
        """TODO: Add docstring."""
        called["close"] = True

    monkeypatch.setattr(Client, "close", fake_close)

    with _create_sdk() as sdk:
        assert isinstance(sdk, sdk_mod.ImednetSDK)

    assert called["close"]


def test_convenience_methods_delegate_to_endpoints(monkeypatch) -> None:
    """TODO: Add docstring."""
    sdk = _create_sdk()
    calls = {}

    def fake_studies_list(study_key=None, **kw):
        """TODO: Add docstring."""
        calls["studies"] = kw
        return ["STUDY"]

    def fake_records_list(study_key, record_data_filter=None, **kw):
        """TODO: Add docstring."""
        calls["records"] = (study_key, record_data_filter, kw)
        return ["REC"]

    def fake_sites_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["sites"] = (study_key, kw)
        return ["SITE"]

    def fake_subjects_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["subjects"] = (study_key, kw)
        return ["SUB"]

    def fake_create(study_key, records_data, email_notify=None, schema=None):
        """TODO: Add docstring."""
        calls["create"] = (study_key, records_data, email_notify)
        return "JOB"

    def fake_forms_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["forms"] = (study_key, kw)
        return ["FORM"]

    def fake_intervals_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["intervals"] = (study_key, kw)
        return ["INT"]

    def fake_variables_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["variables"] = (study_key, kw)
        return ["VAR"]

    def fake_visits_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["visits"] = (study_key, kw)
        return ["VIS"]

    def fake_codings_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["codings"] = (study_key, kw)
        return ["COD"]

    def fake_queries_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["queries"] = (study_key, kw)
        return ["QUERY"]

    def fake_record_revisions_list(study_key, **kw):
        """TODO: Add docstring."""
        calls["record_revisions"] = (study_key, kw)
        return ["REV"]

    def fake_users_list(study_key, include_inactive=False):
        """TODO: Add docstring."""
        calls["users"] = (study_key, include_inactive)
        return ["USER"]

    def fake_get_job(study_key, batch_id):
        """TODO: Add docstring."""
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


def test_poll_job_convenience_sync(monkeypatch) -> None:
    """TODO: Add docstring."""
    sdk = _create_sdk()
    calls = {}

    class FakePoller:
        """TODO: Add docstring."""

        def __init__(self, get_func, **kwargs):
            """TODO: Add docstring."""
            calls["init"] = get_func

        def run(self, study_key, batch_id, interval, timeout):
            """TODO: Add docstring."""
            calls["run"] = (study_key, batch_id, interval, timeout)
            return "JOBOBJ"

    import imednet.sdk_convenience

    monkeypatch.setattr(imednet.sdk_convenience, "JobPoller", FakePoller)

    assert sdk.poll_job("S1", "B1", interval=10, timeout=100) == "JOBOBJ"
    assert calls["run"] == ("S1", "B1", 10, 100)
