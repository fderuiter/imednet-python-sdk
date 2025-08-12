import importlib.util
import os
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

import imednet.cli as cli
from imednet.core.exceptions import ApiError


@pytest.fixture(autouse=True)
def env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required environment variables for each test."""
    monkeypatch.setenv("IMEDNET_API_KEY", "key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "secret")


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def sdk(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Provide a mocked SDK and patch get_sdk."""
    mock_sdk = MagicMock()
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=mock_sdk))
    return mock_sdk


def test_missing_env_vars(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 1
    assert "IMEDNET_API_KEY" in result.stdout


def test_studies_list_success(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.studies.list.return_value = ["study1"]
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 0
    sdk.studies.list.assert_called_once_with()
    assert "study1" in result.stdout


def test_studies_list_api_error(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.studies.list.side_effect = ApiError("boom")
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_sdk_closed_after_command(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.studies.list.return_value = []
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 0
    sdk.close.assert_called_once()


def test_sites_list_success(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.sites.list.return_value = ["site1"]
    result = runner.invoke(cli.app, ["sites", "list", "STUDY"])
    assert result.exit_code == 0
    sdk.sites.list.assert_called_once_with("STUDY")
    assert "site1" in result.stdout


def test_sites_list_missing_argument(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["sites", "list"])
    assert result.exit_code != 0


def test_sites_list_api_error(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.sites.list.side_effect = ApiError("fail")
    result = runner.invoke(cli.app, ["sites", "list", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_subjects_list_success(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.subjects.list.return_value = ["S1"]
    result = runner.invoke(
        cli.app,
        ["subjects", "list", "STUDY", "--filter", "subject_status=Screened"],
    )
    assert result.exit_code == 0
    sdk.subjects.list.assert_called_once_with("STUDY", subject_status="Screened")


def test_subjects_list_invalid_filter(runner: CliRunner, sdk: MagicMock) -> None:
    result = runner.invoke(cli.app, ["subjects", "list", "STUDY", "--filter", "badfilter"])
    assert result.exit_code == 1
    assert "Invalid filter format" in result.stdout
    sdk.subjects.list.assert_not_called()


def test_subjects_list_api_error(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.subjects.list.side_effect = ApiError("boom")
    result = runner.invoke(cli.app, ["subjects", "list", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_extract_records_calls_workflow(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow = MagicMock()
    monkeypatch.setattr(cli, "DataExtractionWorkflow", MagicMock(return_value=workflow))
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


def test_extract_records_api_error(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLI surfaces workflow errors."""
    workflow = MagicMock()
    workflow.extract_records_by_criteria.side_effect = ApiError("fail")
    monkeypatch.setattr(cli, "DataExtractionWorkflow", MagicMock(return_value=workflow))
    result = runner.invoke(cli.app, ["workflows", "extract-records", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_records_list_success(runner: CliRunner, sdk: MagicMock) -> None:
    rec = MagicMock()
    rec.model_dump.return_value = {"recordId": 1, "subjectKey": "S1"}
    sdk.records.list.return_value = [rec]
    result = runner.invoke(cli.app, ["records", "list", "STUDY"])
    assert result.exit_code == 0
    sdk.records.list.assert_called_once_with("STUDY")
    assert "S1" in result.stdout


def test_records_list_output_csv(runner: CliRunner, sdk: MagicMock) -> None:
    rec = MagicMock()
    rec.model_dump.return_value = {"recordId": 1}
    sdk.records.list.return_value = [rec]
    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "csv"])
        assert result.exit_code == 0
        assert os.path.exists("records.csv")
    sdk.records.list.assert_called_once_with("STUDY")


def test_records_list_output_json(runner: CliRunner, sdk: MagicMock) -> None:
    rec = MagicMock()
    rec.model_dump.return_value = {"recordId": 1}
    sdk.records.list.return_value = [rec]
    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "json"])
        assert result.exit_code == 0
        assert os.path.exists("records.json")
    sdk.records.list.assert_called_once_with("STUDY")


def test_records_list_no_records(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.records.list.return_value = []
    result = runner.invoke(cli.app, ["records", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No records found." in result.stdout
    sdk.records.list.assert_called_once_with("STUDY")


def test_records_list_invalid_output(runner: CliRunner, sdk: MagicMock) -> None:
    result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "txt"])
    assert result.exit_code == 1
    assert "Invalid output format" in result.stdout
    sdk.records.list.assert_not_called()


def test_records_list_api_error(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.records.list.side_effect = ApiError("oops")
    result = runner.invoke(cli.app, ["records", "list", "STUDY"])
    assert result.exit_code == 1
    assert "API Error" in result.stdout


def test_export_parquet_calls_helper(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(cli, "export_to_parquet", func)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    result = runner.invoke(cli.app, ["export", "parquet", "STUDY", "out.parquet"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk, "STUDY", "out.parquet")


def test_export_csv_calls_helper(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(cli, "export_to_csv", func)
    result = runner.invoke(cli.app, ["export", "csv", "STUDY", "out.csv"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk, "STUDY", "out.csv")


def test_export_excel_calls_helper(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(cli, "export_to_excel", func)
    result = runner.invoke(cli.app, ["export", "excel", "STUDY", "out.xlsx"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk, "STUDY", "out.xlsx")


def test_export_json_calls_helper(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(cli, "export_to_json", func)
    result = runner.invoke(cli.app, ["export", "json", "STUDY", "out.json"])
    assert result.exit_code == 0
    func.assert_called_once_with(sdk, "STUDY", "out.json")


def test_export_sql_calls_helper_non_sqlite(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(cli, "export_to_sql", func)
    monkeypatch.setattr(cli, "export_to_sql_by_form", MagicMock())
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
        sdk,
        "STUDY",
        "table",
        "postgresql://",
        variable_whitelist=["A", "B"],
        form_whitelist=[1, 2],
    )


def test_export_sql_sqlite_uses_by_form(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    form_func = MagicMock()
    monkeypatch.setattr(cli, "export_to_sql_by_form", form_func)
    monkeypatch.setattr(cli, "export_to_sql", MagicMock())
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
        sdk,
        "STUDY",
        "sqlite://",
        variable_whitelist=["A"],
        form_whitelist=[10],
    )


def test_export_sql_sqlite_single_table(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    form_func = MagicMock()
    single = ["--single-table"]
    monkeypatch.setattr(cli, "export_to_sql_by_form", form_func)
    sql_func = MagicMock()
    monkeypatch.setattr(cli, "export_to_sql", sql_func)
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
        sdk,
        "STUDY",
        "table",
        "sqlite://",
        variable_whitelist=["V1"],
        form_whitelist=[5],
    )
    form_func.assert_not_called()


def test_export_sql_long_format(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    long_func = MagicMock()
    monkeypatch.setattr(cli, "export_to_long_sql", long_func)
    monkeypatch.setattr(cli, "export_to_sql_by_form", MagicMock())
    monkeypatch.setattr(cli, "export_to_sql", MagicMock())
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
    long_func.assert_called_once_with(sdk, "STUDY", "table", "sqlite://")
    cli.export_to_sql.assert_not_called()  # type: ignore[attr-defined]
    cli.export_to_sql_by_form.assert_not_called()  # type: ignore[attr-defined]


def test_export_sql_long_format_overrides_single(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    long_func = MagicMock()
    monkeypatch.setattr(cli, "export_to_long_sql", long_func)
    monkeypatch.setattr(cli, "export_to_sql_by_form", MagicMock())
    monkeypatch.setattr(cli, "export_to_sql", MagicMock())
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
    long_func.assert_called_once_with(sdk, "STUDY", "tbl", "postgresql://")
    cli.export_to_sql.assert_not_called()  # type: ignore[attr-defined]
    cli.export_to_sql_by_form.assert_not_called()  # type: ignore[attr-defined]


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


def test_subject_data_calls_workflow(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow = MagicMock()
    monkeypatch.setattr(cli, "SubjectDataWorkflow", MagicMock(return_value=workflow))
    workflow.get_all_subject_data.return_value = MagicMock()
    result = runner.invoke(cli.app, ["subject-data", "STUDY", "SUBJ"])
    assert result.exit_code == 0
    workflow.get_all_subject_data.assert_called_once_with("STUDY", "SUBJ")


def test_queries_list_success(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.queries.list.return_value = ["Q1"]
    result = runner.invoke(cli.app, ["queries", "list", "STUDY"])
    assert result.exit_code == 0
    sdk.queries.list.assert_called_once_with("STUDY")
    assert "Found 1 queries:" in result.stdout
    assert "Q1" in result.stdout


def test_queries_list_empty(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.queries.list.return_value = []
    result = runner.invoke(cli.app, ["queries", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No queries found." in result.stdout


def test_variables_list_success(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.variables.list.return_value = ["V1"]
    result = runner.invoke(cli.app, ["variables", "list", "STUDY"])
    assert result.exit_code == 0
    sdk.variables.list.assert_called_once_with("STUDY")
    assert "Found 1 variables:" in result.stdout
    assert "V1" in result.stdout


def test_variables_list_empty(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.variables.list.return_value = []
    result = runner.invoke(cli.app, ["variables", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No variables found." in result.stdout


def test_record_revisions_list_success(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.record_revisions.list.return_value = ["R1"]
    result = runner.invoke(cli.app, ["record-revisions", "list", "STUDY"])
    assert result.exit_code == 0
    sdk.record_revisions.list.assert_called_once_with("STUDY")
    assert "Found 1 record revisions:" in result.stdout
    assert "R1" in result.stdout


def test_record_revisions_list_empty(runner: CliRunner, sdk: MagicMock) -> None:
    sdk.record_revisions.list.return_value = []
    result = runner.invoke(cli.app, ["record-revisions", "list", "STUDY"])
    assert result.exit_code == 0
    assert "No record revisions found." in result.stdout


def test_jobs_status_success(runner: CliRunner, sdk: MagicMock) -> None:
    result = runner.invoke(cli.app, ["jobs", "status", "STUDY", "BATCH"])
    assert result.exit_code == 0
    sdk.get_job.assert_called_once_with("STUDY", "BATCH")


def test_jobs_wait_success(runner: CliRunner, sdk: MagicMock) -> None:
    result = runner.invoke(cli.app, ["jobs", "wait", "STUDY", "BATCH"])
    assert result.exit_code == 0
    sdk.poll_job.assert_called_once_with("STUDY", "BATCH", interval=5, timeout=300)
