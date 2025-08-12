import pandas as pd
import pytest
from typer.testing import CliRunner

from imednet import cli
from imednet.integrations import export as export_mod


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


def test_cli_export_sql_chunks_tables(
    runner: CliRunner, study_key: str, tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import create_engine, inspect, text

    out_db = tmp_path / "test.db"
    columns = [f"c{i}" for i in range(export_mod.MAX_SQLITE_COLUMNS + 1)]
    df = pd.DataFrame({c: [i] for i, c in enumerate(columns)})
    monkeypatch.setattr(export_mod, "_records_df", lambda *a, **k: df)
    result = runner.invoke(
        cli.app,
        [
            "export",
            "sql",
            study_key,
            "table",
            f"sqlite:///{out_db}",
            "--single-table",
        ],
    )
    assert result.exit_code == 0
    engine = create_engine(f"sqlite:///{out_db}")
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    assert "table_part1" in table_names
    assert "table_part2" in table_names
    with engine.connect() as conn:
        for t in ("table_part1", "table_part2"):
            count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            assert count == 1


def test_cli_workflows_extract(runner: CliRunner, study_key: str) -> None:
    result = runner.invoke(cli.app, ["workflows", "extract-records", study_key])
    assert result.exit_code == 0
