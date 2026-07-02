"""Unit tests for sqlite export modes."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

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


import imednet.cli as cli
from imednet.integrations import export as export_mod


@pytest.fixture
def sqlite_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Helper function to sqlite env."""
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    engine = MagicMock()
    engine.dialect.name = "sqlite"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)


def _setup_per_form_mapper(monkeypatch: pytest.MonkeyPatch) -> None:
    """Helper function to  setup per form mapper."""
    form1_vars = [MagicMock(variable_name=f"v{i}", label=f"v{i}") for i in range(1500)]
    form2_vars = [MagicMock(variable_name=f"w{i}", label=f"w{i}") for i in range(600)]
    sdk = MagicMock()
    sdk.forms.list.return_value = [
        MagicMock(form_id=1, form_key="F1"),
        MagicMock(form_id=2, form_key="F2"),
    ]
    sdk.variables.list.side_effect = [form1_vars, form2_vars]

    mapper_inst = MagicMock()
    mapper_inst._build_record_model.return_value = object()
    mapper_inst._fetch_records.side_effect = [MagicMock(), MagicMock()]
    rows1 = [{f"v{i}": i for i in range(1500)}]
    rows2 = [{f"w{i}": i for i in range(600)}]
    mapper_inst._parse_records.side_effect = [(rows1, 0), (rows2, 0)]
    mapper_inst._build_dataframe.side_effect = [pd.DataFrame(rows1), pd.DataFrame(rows2)]
    monkeypatch.setattr(
        export_mod, "_record_mapper", MagicMock(return_value=MagicMock(return_value=mapper_inst))
    )
    monkeypatch.setattr("imednet.cli.utils.context.get_sdk", MagicMock(return_value=sdk))
    monkeypatch.setattr(pd.DataFrame, "to_sql", MagicMock())


def _setup_single_table_mapper(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Helper function to  setup single table mapper."""
    columns = [f"c{i}" for i in range(2100)]
    df = pd.DataFrame([range(2100)], columns=columns)
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    monkeypatch.setattr(
        export_mod, "_record_mapper", MagicMock(return_value=MagicMock(return_value=mapper_inst))
    )
    monkeypatch.setattr("imednet.cli.utils.context.get_sdk", MagicMock(return_value=MagicMock()))
    mock_to_sql = MagicMock()
    monkeypatch.setattr(pd.DataFrame, "to_sql", mock_to_sql)
    return mock_to_sql


def test_default_sqlite_mode_splits_by_form(
    sqlite_env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that default sqlite mode splits by form."""
    _setup_per_form_mapper(monkeypatch)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        cli.app,
        ["export", "sql", "STUDY", "unused", "sqlite:///db.sqlite"],
    )
    assert result.exit_code == 0


def test_single_table_mode_chunks(
    sqlite_env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that single table mode chunks."""
    mock_to_sql = _setup_single_table_mapper(monkeypatch)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        cli.app,
        ["export", "sql", "STUDY", "table", "sqlite:///db.sqlite", "--single-table"],
    )
    assert result.exit_code == 0
    assert mock_to_sql.call_count == 2
    calls = mock_to_sql.call_args_list
    assert calls[0].args[0] == "table_part1"
    assert calls[1].args[0] == "table_part2"
