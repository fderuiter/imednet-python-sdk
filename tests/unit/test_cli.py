import builtins
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

import imednet.cli as cli


def _setup_env(monkeypatch):
    monkeypatch.setenv("IMEDNET_API_KEY", "key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "secret")


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_missing_env_vars(runner, monkeypatch):
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 1
    assert "IMEDNET_API_KEY" in result.stdout


def test_list_studies_calls_sdk(runner, monkeypatch):
    _setup_env(monkeypatch)
    mock_sdk = MagicMock()
    mock_sdk.studies.list.return_value = ["study1"]
    monkeypatch.setattr(cli, "ImednetSDK", MagicMock(return_value=mock_sdk))
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 0
    assert "study1" in result.stdout
    mock_sdk.studies.list.assert_called_once_with()


def test_sites_list_requires_argument(runner):
    result = runner.invoke(cli.app, ["sites", "list"])  # missing study_key
    assert result.exit_code != 0


def test_subjects_list_with_filter(runner, monkeypatch):
    _setup_env(monkeypatch)
    mock_sdk = MagicMock()
    mock_sdk.subjects.list.return_value = []
    monkeypatch.setattr(cli, "ImednetSDK", MagicMock(return_value=mock_sdk))
    result = runner.invoke(
        cli.app,
        ["subjects", "list", "STUDY", "--filter", "subject_status=Screened"],
    )
    assert result.exit_code == 0
    mock_sdk.subjects.list.assert_called_once_with(
        "STUDY", filter="subject_status==Screened"
    )


def test_invalid_filter_reports_error(runner, monkeypatch):
    _setup_env(monkeypatch)
    monkeypatch.setattr(cli, "ImednetSDK", MagicMock(return_value=MagicMock()))
    result = runner.invoke(
        cli.app,
        ["subjects", "list", "STUDY", "--filter", "badfilter"],
    )
    assert result.exit_code == 1
    assert "Invalid filter format" in result.stdout


def test_extract_records_calls_workflow(runner, monkeypatch):
    _setup_env(monkeypatch)
    mock_sdk = MagicMock()
    monkeypatch.setattr(cli, "ImednetSDK", MagicMock(return_value=mock_sdk))
    workflow_instance = MagicMock()
    monkeypatch.setattr(cli, "DataExtractionWorkflow", MagicMock(return_value=workflow_instance))
    workflow_instance.extract_records_by_criteria.return_value = [1, 2]
    result = runner.invoke(
        cli.app,
        [
            "workflows",
            "extract-records",
            "STUDY",
            "--record-filter",
            "form_key=DEMOG",
        ],
    )
    assert result.exit_code == 0
    workflow_instance.extract_records_by_criteria.assert_called_once_with(
        study_key="STUDY",
        record_filter={"form_key": "DEMOG"},
        subject_filter=None,
        visit_filter=None,
    )

