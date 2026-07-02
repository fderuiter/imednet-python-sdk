"""Unit tests for cli live."""

import pandas as pd
import pytest


class Result:
    def __init__(self, exit_code, stdout, stderr=""):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.output = stdout + stderr

class CliRunner:
    def invoke(self, app, args):
        import io
        import sys
        from contextlib import redirect_stderr, redirect_stdout
        out = io.StringIO()
        err = io.StringIO()
        exit_code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                if hasattr(app, "parse_args"):
                    pass
                app(args)
        except SystemExit as e:
            exit_code = e.code or 0
        except Exception as e:
            import traceback
            err.write(traceback.format_exc())
            exit_code = 1
        
        # We also need to catch argparse sys.exit(2)
        return Result(exit_code, out.getvalue(), err.getvalue())



from imednet import cli
from imednet.integrations import export as export_mod


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    """Helper function to runner."""
    return CliRunner()


def test_cli_studies_list(runner: CliRunner) -> None:
    """Test that cli studies list."""
    result = runner.invoke(cli.app, ["studies", "list"])
    assert result.exit_code == 0


def test_cli_sites_list(runner: CliRunner, study_key: str) -> None:
    """Test that cli sites list."""
    result = runner.invoke(cli.app, ["sites", "list", study_key])
    assert result.exit_code == 0


def test_cli_subjects_list(runner: CliRunner, study_key: str) -> None:
    """Test that cli subjects list."""
    result = runner.invoke(cli.app, ["subjects", "list", study_key])
    assert result.exit_code == 0


def test_cli_records_list(runner: CliRunner, study_key: str) -> None:
    """Test that cli records list."""
    result = runner.invoke(cli.app, ["records", "list", study_key])
    assert result.exit_code == 0


def test_cli_jobs_status(runner: CliRunner, study_key: str, generated_batch_id: str) -> None:
    """Test that cli jobs status."""
    result = runner.invoke(
        cli.app,
        ["jobs", "status", study_key, generated_batch_id],
    )
    assert result.exit_code == 0


def test_cli_jobs_wait(runner: CliRunner, study_key: str, generated_batch_id: str) -> None:
    """Test that cli jobs wait."""
    result = runner.invoke(
        cli.app,
        ["jobs", "wait", study_key, generated_batch_id, "--interval", "1", "--timeout", "60"],
    )
    assert result.exit_code == 0


def test_cli_export_parquet(runner: CliRunner, study_key: str, tmp_path) -> None:
    """Test that cli export parquet."""
    pytest.importorskip("pyarrow")
    out = tmp_path / "data.parquet"
    result = runner.invoke(cli.app, ["export", "parquet", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_csv(runner: CliRunner, study_key: str, tmp_path) -> None:
    """Test that cli export csv."""
    out = tmp_path / "data.csv"
    result = runner.invoke(cli.app, ["export", "csv", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_excel(runner: CliRunner, study_key: str, tmp_path) -> None:
    """Test that cli export excel."""
    pytest.importorskip("openpyxl")
    out = tmp_path / "data.xlsx"
    result = runner.invoke(cli.app, ["export", "excel", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_json(runner: CliRunner, study_key: str, tmp_path) -> None:
    """Test that cli export json."""
    out = tmp_path / "data.json"
    result = runner.invoke(cli.app, ["export", "json", study_key, str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_export_sql_chunks_tables(
    runner: CliRunner, study_key: str, tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that cli export sql chunks tables."""
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
    """Test that cli workflows extract."""
    result = runner.invoke(cli.app, ["workflows", "extract-records", study_key])
    assert result.exit_code == 0
