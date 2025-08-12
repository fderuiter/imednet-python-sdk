import pytest
from typer.testing import CliRunner

from imednet import cli


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()


def test_cli_studies_list(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 0


def test_cli_sites_list(runner: CliRunner, study_key: str) -> None:
    result = runner.invoke(cli.app, ["sites", "list", study_key])
    assert result.exit_code == 0


def test_cli_subjects_list(runner: CliRunner, study_key: str) -> None:
    result = runner.invoke(cli.app, ["subjects", "list", study_key])
    assert result.exit_code == 0


def test_cli_records_list(runner: CliRunner, study_key: str) -> None:
    result = runner.invoke(cli.app, ["records", "list", study_key])
    assert result.exit_code == 0


def test_cli_jobs_status(runner: CliRunner, study_key: str, generated_batch_id: str) -> None:
    result = runner.invoke(
        cli.app,
        ["jobs", "status", study_key, generated_batch_id],
    )
    assert result.exit_code == 0


def test_cli_jobs_wait(runner: CliRunner, study_key: str, generated_batch_id: str) -> None:
    result = runner.invoke(
        cli.app,
        ["jobs", "wait", study_key, generated_batch_id],
    )
    assert result.exit_code == 0


def test_cli_export_parquet(runner: CliRunner, study_key: str, tmp_path) -> None:
    pytest.importorskip("pyarrow")
    out = tmp_path / "data.parquet"
    result = runner.invoke(cli.app, ["export", "parquet", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_csv(runner: CliRunner, study_key: str, tmp_path) -> None:
    out = tmp_path / "data.csv"
    result = runner.invoke(cli.app, ["export", "csv", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_excel(runner: CliRunner, study_key: str, tmp_path) -> None:
    pytest.importorskip("openpyxl")
    out = tmp_path / "data.xlsx"
    result = runner.invoke(cli.app, ["export", "excel", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_json(runner: CliRunner, study_key: str, tmp_path) -> None:
    out = tmp_path / "data.json"
    result = runner.invoke(cli.app, ["export", "json", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_sql(runner: CliRunner, study_key: str, tmp_path) -> None:
    pytest.importorskip("sqlalchemy")
    out_db = tmp_path / "test.db"
    result = runner.invoke(cli.app, ["export", "sql", study_key, "table", f"sqlite:///{out_db}"])
    assert result.exit_code == 0
    assert out_db.exists()


def test_cli_workflows_extract(runner: CliRunner, study_key: str) -> None:
    result = runner.invoke(cli.app, ["workflows", "extract-records", study_key])
    assert result.exit_code == 0
