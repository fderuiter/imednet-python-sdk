import os

import pytest
from imednet import cli
from imednet.sdk import ImednetSDK
from typer.testing import CliRunner

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")
RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_E2E or not (API_KEY and SECURITY_KEY),
    reason=(
        "Set IMEDNET_RUN_E2E=1 and provide IMEDNET_API_KEY/IMEDNET_SECURITY_KEY to run live tests"
    ),
)


@pytest.fixture(scope="module")
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="module")
def study_key() -> str:
    with ImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL) as sdk:
        studies = sdk.get_studies()
    if not studies:
        pytest.skip("No studies available for CLI tests")
    return studies[0].study_key


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


def test_cli_jobs_status(runner: CliRunner, study_key: str) -> None:
    batch_id = os.getenv("IMEDNET_BATCH_ID")
    if not batch_id:
        pytest.skip("IMEDNET_BATCH_ID not set")
    result = runner.invoke(cli.app, ["jobs", "status", study_key, batch_id])
    assert result.exit_code == 0


def test_cli_jobs_wait(runner: CliRunner, study_key: str) -> None:
    batch_id = os.getenv("IMEDNET_BATCH_ID")
    if not batch_id:
        pytest.skip("IMEDNET_BATCH_ID not set")
    result = runner.invoke(cli.app, ["jobs", "wait", study_key, batch_id])
    assert result.exit_code == 0


def test_cli_export_parquet(runner: CliRunner, study_key: str, tmp_path) -> None:
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
    out_db = tmp_path / "test.db"
    result = runner.invoke(cli.app, ["export", "sql", study_key, "table", f"sqlite:///{out_db}"])
    assert result.exit_code == 0
    assert out_db.exists()


def test_cli_workflows_extract(runner: CliRunner, study_key: str) -> None:
    result = runner.invoke(cli.app, ["workflows", "extract-records", study_key])
    assert result.exit_code == 0
