from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

import imednet.cli as cli


def test_cli_rejects_missing_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)

    result = runner.invoke(cli.app, ["studies", "list"])

    assert result.exit_code == 1
    assert "IMEDNET_API_KEY" in result.stdout


def test_studies_list_success(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")

    sdk = MagicMock()
    sdk.studies.list.return_value = ["study1"]
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=sdk))

    result = runner.invoke(cli.app, ["studies", "list"])

    assert result.exit_code == 0
    sdk.studies.list.assert_called_once_with()
    assert "study1" in result.stdout


def test_records_list_output_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")

    record = MagicMock()
    record.model_dump.return_value = {"id": 1}
    sdk = MagicMock()
    sdk.records.list.return_value = [record]
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=sdk))

    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["records", "list", "ST", "--output", "csv"])
        assert result.exit_code == 0
        assert Path("records.csv").exists()
    sdk.records.list.assert_called_once_with("ST")


def test_extract_records_cli_parses_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")

    workflow = MagicMock()
    workflow.extract_records_by_criteria.return_value = [1]
    monkeypatch.setattr(cli, "DataExtractionWorkflow", MagicMock(return_value=workflow))
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=MagicMock()))

    result = runner.invoke(
        cli.app,
        [
            "workflows",
            "extract-records",
            "ST",
            "--record-filter",
            "form_key=DEMOG",
            "--subject-filter",
            "subject_status=Screened",
            "--visit-filter",
            "visit_key=BASE",
        ],
    )

    assert result.exit_code == 0
    workflow.extract_records_by_criteria.assert_called_once_with(
        study_key="ST",
        record_filter={"form_key": "DEMOG"},
        subject_filter={"subject_status": "Screened"},
        visit_filter={"visit_key": "BASE"},
    )


def test_invalid_filter_string(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=MagicMock()))

    result = runner.invoke(cli.app, ["subjects", "list", "ST", "--filter", "badfilter"])

    assert result.exit_code == 1
    assert "Invalid filter format" in result.stdout
