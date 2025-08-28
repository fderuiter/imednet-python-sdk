import importlib.util
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pandas as pd
import pytest
from typer.testing import CliRunner

import imednet.cli as cli
from imednet.integrations import export as export_mod


@pytest.fixture
def sqlite_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    engine = MagicMock()
    engine.dialect.name = "sqlite"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)


def _setup_per_form_mapper(monkeypatch: pytest.MonkeyPatch) -> None:
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
    monkeypatch.setattr(export_mod, "RecordMapper", MagicMock(return_value=mapper_inst))
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=sdk))
    monkeypatch.setattr(pd.DataFrame, "to_sql", MagicMock())


def _setup_single_table_mapper(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    columns = [f"c{i}" for i in range(2100)]
    df = pd.DataFrame([range(2100)], columns=columns)
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    monkeypatch.setattr(export_mod, "RecordMapper", MagicMock(return_value=mapper_inst))
    monkeypatch.setattr("imednet.cli.decorators.ImednetSDK", MagicMock(return_value=MagicMock()))
    mock_to_sql = MagicMock()
    monkeypatch.setattr(pd.DataFrame, "to_sql", mock_to_sql)
    return mock_to_sql


def test_default_sqlite_mode_splits_by_form(sqlite_env, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup_per_form_mapper(monkeypatch)
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli.app,
            ["export", "sql", "STUDY", "unused", "sqlite:///db.sqlite"],
        )
    assert result.exit_code == 0


def test_single_table_mode_chunks(sqlite_env, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_to_sql = _setup_single_table_mapper(monkeypatch)
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli.app,
            ["export", "sql", "STUDY", "table", "sqlite:///db.sqlite", "--single-table"],
        )
    assert result.exit_code == 0
    assert mock_to_sql.call_count == 2
    calls = mock_to_sql.call_args_list
    assert calls[0].args[0] == "table_part1"
    assert calls[1].args[0] == "table_part2"
