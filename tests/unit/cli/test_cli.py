import os
from unittest.mock import MagicMock

import imednet.cli as cli
import pytest
from imednet.core.exceptions import ApiError
from typer.testing import CliRunner


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
    sdk.subjects.list.assert_called_once_with("STUDY", filter="subject_status==Screened")


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


def test_export_sql_calls_helper(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(cli, "export_to_sql", func)
    result = runner.invoke(
        cli.app,
        ["export", "sql", "STUDY", "table", "sqlite://"],
    )
    assert result.exit_code == 0
    func.assert_called_once_with(sdk, "STUDY", "table", "sqlite://")


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