import importlib.util
import os
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

import imednet.cli as cli
from imednet.core.exceptions import ApiError
from imednet.integrations import export as export_mod
from imednet.models.error import ApiErrorDetail


@pytest.fixture(autouse=True)
def env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required environment variables for each test."""
    monkeypatch.setenv("IMEDNET_API_KEY", "key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "secret")


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_missing_env_vars(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 1
    assert "Error: API key and security key are required" in result.stdout


def test_studies_list_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.studies.list.return_value = ["study1"]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 0
    sdk_mock.studies.list.assert_called_once_with()
    assert "study1" in result.stdout


def test_studies_list_api_error(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.studies.list.side_effect = ApiError(ApiErrorDetail(detail="boom"))
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_sdk_closed_after_command(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.studies.list.return_value = []
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 0
    sdk_mock.close.assert_called_once()


def test_multiple_invocations_close_sdk(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.studies.list.return_value = []
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    first = runner.invoke(cli.app, ["studies", "list"])
    second = runner.invoke(cli.app, ["studies", "list"])
    assert first.exit_code == 0 and second.exit_code == 0
    assert sdk_mock.close.call_count == 2


def test_sites_list_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.sites.list.return_value = ["site1"]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["sites", "list", "STUDY"])
    assert result.exit_code == 0
    sdk_mock.sites.list.assert_called_once_with("STUDY")
    assert "site1" in result.stdout


def test_sites_list_missing_argument(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["sites", "list"])
    assert result.exit_code != 0


def test_sites_list_api_error(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.sites.list.side_effect = ApiError(ApiErrorDetail(detail="fail"))
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["sites", "list", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_subjects_list_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.subjects.list.return_value = ["S1"]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(
        cli.app,
        ["subjects", "list", "STUDY", "--filter", "subject_status=Screened"],
    )
    assert result.exit_code == 0
    sdk_mock.subjects.list.assert_called_once_with("STUDY", subject_status="Screened")


def test_subjects_list_invalid_filter(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["subjects", "list", "STUDY", "--filter", "badfilter"])
    assert result.exit_code == 1
    assert "Invalid filter format" in result.stdout
    sdk_mock.subjects.list.assert_not_called()


def test_subjects_list_api_error(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.subjects.list.side_effect = ApiError(ApiErrorDetail(detail="boom"))
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["subjects", "list", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_extract_records_calls_workflow(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    workflow = MagicMock()
    monkeypatch.setattr(
        "imednet.workflows.data_extraction.DataExtractionWorkflow",
        MagicMock(return_value=workflow),
    )
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    workflow.extract_records_by_criteria.return_value = [1]
    result = runner.invoke(
        cli.app,
        ["workflows", "extract-records", "STUDY", "--record-filter", "form_key=DEMOG"],
    )
    assert result.exit_code == 0
    workflow.extract_records_by_criteria.assert_called_once_with(
        study_key="STUDY",
        record_filter={"form_key": "DEMOG"},
        subject_filter=None,
        visit_filter=None,
    )


def test_extract_records_api_error(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI surfaces workflow errors."""
    sdk_mock = MagicMock()
    workflow = MagicMock()
    workflow.extract_records_by_criteria.side_effect = ApiError(ApiErrorDetail(detail="fail"))
    monkeypatch.setattr(
        "imednet.workflows.data_extraction.DataExtractionWorkflow",
        MagicMock(return_value=workflow),
    )
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["workflows", "extract-records", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_records_list_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    rec = MagicMock()
    rec.model_dump.return_value = {"recordId": 1, "subjectKey": "S1"}
    sdk_mock.records.list.return_value = [rec]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["records", "list", "STUDY"])
    assert result.exit_code == 0
    sdk_mock.records.list.assert_called_once_with("STUDY")
    assert "S1" in result.stdout


def test_records_list_output_csv(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    rec = MagicMock()
    rec.model_dump.return_value = {"recordId": 1}
    sdk_mock.records.list.return_value = [rec]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "csv"])
        assert result.exit_code == 0
        assert os.path.exists("records.csv")
    sdk_mock.records.list.assert_called_once_with("STUDY")


def test_records_list_output_json(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    rec = MagicMock()
    rec.model_dump.return_value = {"recordId": 1}
    sdk_mock.records.list.return_value = [rec]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "json"])
        assert result.exit_code == 0
        assert os.path.exists("records.json")
    sdk_mock.records.list.assert_called_once_with("STUDY")


def test_records_list_no_records(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.records.list.return_value = []
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["records", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No records found." in result.stdout
    sdk_mock.records.list.assert_called_once_with("STUDY")


def test_records_list_invalid_output(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "txt"])
    assert result.exit_code == 1
    assert "Invalid output format" in result.stdout
    sdk_mock.records.list.assert_not_called()


def test_records_list_api_error(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.records.list.side_effect = ApiError(ApiErrorDetail(detail="oops"))
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["records", "list", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_export_parquet_calls_helper(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_parquet", func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    result = runner.invoke(cli.app, ["export", "parquet", "STUDY", "out.parquet"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk_mock, "STUDY", "out.parquet")


def test_export_csv_calls_helper(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_csv", func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["export", "csv", "STUDY", "out.csv"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk_mock, "STUDY", "out.csv")


def test_export_excel_calls_helper(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_excel", func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["export", "excel", "STUDY", "out.xlsx"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk_mock, "STUDY", "out.xlsx")


def test_export_json_calls_helper(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_json", func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["export", "json", "STUDY", "out.json"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk_mock, "STUDY", "out.json")


def test_export_sql_calls_helper_non_sqlite(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    sdk_mock = MagicMock()
    func = MagicMock()
    form_func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_sql", func)
    monkeypatch.setattr(export_mod, "export_to_sql_by_form", form_func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    engine = MagicMock()
    engine.dialect.name = "postgres"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)
    result = runner.invoke(
        cli.app,
        [
            "export",
            "sql",
            "STUDY",
            "table",
            "postgresql://",
            "--vars",
            "A,B",
            "--forms",
            "1,2",
        ],
    )
    assert result.exit_code == 0
    func.assert_called_once_with(
        sdk_mock,
        "STUDY",
        "table",
        "postgresql://",
        variable_whitelist=["A", "B"],
        form_whitelist=[1, 2],
    )


def test_export_sql_sqlite_uses_by_form(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    form_func = MagicMock()
    sql_func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_sql_by_form", form_func)
    monkeypatch.setattr(export_mod, "export_to_sql", sql_func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    engine = MagicMock()
    engine.dialect.name = "sqlite"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)
    result = runner.invoke(
        cli.app,
        [
            "export",
            "sql",
            "STUDY",
            "table",
            "sqlite://",
            "--vars",
            "A",
            "--forms",
            "10",
        ],
    )
    assert result.exit_code == 0
    form_func.assert_called_once_with(
        sdk_mock,
        "STUDY",
        "sqlite://",
        variable_whitelist=["A"],
        form_whitelist=[10],
    )


def test_export_sql_sqlite_single_table(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    form_func = MagicMock()
    single = ["--single-table"]
    sql_func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_sql_by_form", form_func)
    monkeypatch.setattr(export_mod, "export_to_sql", sql_func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    engine = MagicMock()
    engine.dialect.name = "sqlite"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)
    result = runner.invoke(
        cli.app,
        [
            "export",
            "sql",
            "STUDY",
            "table",
            "sqlite://",
            "--vars",
            "V1",
            "--forms",
            "5",
        ]
        + single,
    )
    assert result.exit_code == 0
    sql_func.assert_called_once_with(
        sdk_mock,
        "STUDY",
        "table",
        "sqlite://",
        variable_whitelist=["V1"],
        form_whitelist=[5],
    )
    form_func.assert_not_called()


def test_export_sql_long_format(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    long_func = MagicMock()
    form_func = MagicMock()
    sql_func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_long_sql", long_func)
    monkeypatch.setattr(export_mod, "export_to_sql_by_form", form_func)
    monkeypatch.setattr(export_mod, "export_to_sql", sql_func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    engine = MagicMock()
    engine.dialect.name = "sqlite"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)
    result = runner.invoke(
        cli.app,
        ["export", "sql", "STUDY", "table", "sqlite://", "--long-format"],
    )
    assert result.exit_code == 0
    long_func.assert_called_once_with(sdk_mock, "STUDY", "table", "sqlite://")
    sql_func.assert_not_called()
    form_func.assert_not_called()


def test_export_sql_long_format_overrides_single(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    sdk_mock = MagicMock()
    long_func = MagicMock()
    form_func = MagicMock()
    sql_func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_long_sql", long_func)
    monkeypatch.setattr(export_mod, "export_to_sql_by_form", form_func)
    monkeypatch.setattr(export_mod, "export_to_sql", sql_func)
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    engine = MagicMock()
    engine.dialect.name = "postgres"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)
    result = runner.invoke(
        cli.app,
        [
            "export",
            "sql",
            "STUDY",
            "tbl",
            "postgresql://",
            "--single-table",
            "--long-format",
        ],
    )
    assert result.exit_code == 0
    long_func.assert_called_once_with(sdk_mock, "STUDY", "tbl", "postgresql://")
    sql_func.assert_not_called()
    form_func.assert_not_called()


def test_export_parquet_missing_pyarrow(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str) -> object | None:
        if name == "pyarrow":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = runner.invoke(cli.app, ["export", "parquet", "STUDY", "out.parquet"])
    assert result.exit_code == 1
    assert "pyarrow is required" in result.stdout


def test_export_sql_missing_sqlalchemy(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str) -> object | None:
        if name == "sqlalchemy":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = runner.invoke(
        cli.app,
        ["export", "sql", "STUDY", "table", "sqlite://"],
    )
    assert result.exit_code == 1
    assert "SQLAlchemy is required" in result.stdout


def test_subject_data_calls_workflow(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    workflow = MagicMock()
    monkeypatch.setattr(
        "imednet.workflows.subject_data.SubjectDataWorkflow", MagicMock(return_value=workflow)
    )
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    workflow.get_all_subject_data.return_value = MagicMock()
    result = runner.invoke(cli.app, ["subject-data", "STUDY", "SUBJ"])
    assert result.exit_code == 0
    workflow.get_all_subject_data.assert_called_once_with("STUDY", "SUBJ")


def test_queries_list_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.queries.list.return_value = ["Q1"]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["queries", "list", "STUDY"])
    assert result.exit_code == 0
    sdk_mock.queries.list.assert_called_once_with("STUDY")
    assert "Found 1 queries:" in result.stdout
    assert "Q1" in result.stdout


def test_queries_list_empty(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.queries.list.return_value = []
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["queries", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No queries found." in result.stdout


def test_variables_list_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.variables.list.return_value = ["V1"]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["variables", "list", "STUDY"])
    assert result.exit_code == 0
    sdk_mock.variables.list.assert_called_once_with("STUDY")
    assert "Found 1 variables:" in result.stdout
    assert "V1" in result.stdout


def test_variables_list_empty(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.variables.list.return_value = []
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["variables", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No variables found." in result.stdout


def test_record_revisions_list_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.record_revisions.list.return_value = ["R1"]
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["record-revisions", "list", "STUDY"])
    assert result.exit_code == 0
    sdk_mock.record_revisions.list.assert_called_once_with("STUDY")
    assert "Found 1 record revisions:" in result.stdout
    assert "R1" in result.stdout


def test_record_revisions_list_empty(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    sdk_mock.record_revisions.list.return_value = []
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["record-revisions", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No record revisions found." in result.stdout


def test_jobs_status_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["jobs", "status", "STUDY", "BATCH"])
    assert result.exit_code == 0
    sdk_mock.get_job.assert_called_once_with("STUDY", "BATCH")


def test_jobs_wait_success(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk_mock = MagicMock()
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk_mock))
    result = runner.invoke(cli.app, ["jobs", "wait", "STUDY", "BATCH"])
    assert result.exit_code == 0
    sdk_mock.poll_job.assert_called_once_with("STUDY", "BATCH", interval=5, timeout=300)
