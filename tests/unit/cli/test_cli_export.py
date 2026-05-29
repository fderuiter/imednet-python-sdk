import importlib.util
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

import imednet.cli as cli
import imednet.integrations as integrations_mod
from imednet.integrations import SinkConfig
from unittest.mock import ANY
from imednet_sinks import Neo4jSinkConfig, SnowflakeSinkConfig
from imednet.integrations import export as export_mod


@pytest.fixture(autouse=True)
def env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "secret")


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def sdk(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock_sdk = MagicMock()
    monkeypatch.setattr("imednet.cli.utils.context.get_sdk", MagicMock(return_value=mock_sdk))
    return mock_sdk


def test_cli_export_duckdb_happy_path(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_duckdb", func)
    monkeypatch.setattr(cli, "export_to_duckdb", export_mod.export_to_duckdb)
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())

    result = runner.invoke(
        cli.app,
        ["export", "duckdb", "STUDY", "study_records", "out.duckdb"],
    )

    assert result.exit_code == 0
    func.assert_called_once_with(
        sdk,
        "STUDY",
        "out.duckdb",
        "study_records",
        use_labels_as_columns=False,
        variable_whitelist=None,
        form_whitelist=None,
    )


def test_cli_export_duckdb_missing_dependency(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str) -> object | None:
        if name == "duckdb":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    result = runner.invoke(
        cli.app,
        ["export", "duckdb", "STUDY", "table", "out.duckdb"],
    )

    assert result.exit_code == 1
    assert "imednet[duckdb]" in result.stdout


def test_cli_export_duckdb_vars_forms_passthrough(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    func = MagicMock()
    monkeypatch.setattr(export_mod, "export_to_duckdb", func)
    monkeypatch.setattr(cli, "export_to_duckdb", export_mod.export_to_duckdb)
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())

    result = runner.invoke(
        cli.app,
        [
            "export",
            "duckdb",
            "STUDY",
            "study_records",
            "out.duckdb",
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
        "out.duckdb",
        "study_records",
        use_labels_as_columns=False,
        variable_whitelist=["A", "B"],
        form_whitelist=[1, 2],
    )


def test_cli_export_mongodb_happy_path(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())

    result = runner.invoke(
        cli.app,
        [
            "export",
            "mongodb",
            "STUDY",
            "mongodb://localhost:27017",
            "imednet",
            "records",
            "--batch-size",
            "100",
            "--insert-only",
        ],
    )

    assert result.exit_code == 0
    sdk.sinks.export_to_mongodb.assert_called_once_with(
        sdk,
        "STUDY",
        "mongodb://localhost:27017",
        "imednet",
        "records",
        config=SinkConfig(batch_size=100, idempotent=False),
    )


def test_cli_export_mongodb_missing_dependency(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str) -> object | None:
        if name == "pymongo":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = runner.invoke(
        cli.app,
        ["export", "mongodb", "STUDY", "mongodb://localhost:27017", "db", "records"],
    )

    assert result.exit_code == 1
    assert "imednet[mongodb]" in result.stdout


def test_cli_export_neo4j_happy_path(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    sdk.sinks.Neo4jSinkConfig = Neo4jSinkConfig
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())

    result = runner.invoke(
        cli.app,
        [
            "export",
            "neo4j",
            "STUDY",
            "bolt://localhost:7687",
            "neo4j",
            "password",
            "--database",
            "analytics",
            "--batch-size",
            "250",
            "--create-only",
        ],
    )

    assert result.exit_code == 0
    sdk.sinks.export_to_neo4j.assert_called_once_with(
        sdk,
        "STUDY",
        "bolt://localhost:7687",
        ("neo4j", "password"),
        config=Neo4jSinkConfig(batch_size=250, idempotent=False, database="analytics"),
    )


def test_cli_export_neo4j_missing_dependency(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str) -> object | None:
        if name == "neo4j":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = runner.invoke(
        cli.app,
        ["export", "neo4j", "STUDY", "bolt://localhost:7687", "neo4j", "password"],
    )

    assert result.exit_code == 1
    assert "imednet[neo4j]" in result.stdout


def test_cli_export_snowflake_happy_path(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    sdk.sinks.SnowflakeSinkConfig = SnowflakeSinkConfig
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())

    result = runner.invoke(
        cli.app,
        [
            "export",
            "snowflake",
            "STUDY",
            "acct",
            "user",
            "secret",
            "DB",
            "PUBLIC",
            "WH",
            "STAGE",
            "TBL",
            "--stage-prefix",
            "imednet/dev",
            "--batch-size",
            "200",
            "--force-reload",
        ],
    )

    assert result.exit_code == 0
    sdk.sinks.export_to_snowflake.assert_called_once_with(
        sdk,
        "STUDY",
        config=SnowflakeSinkConfig(
            account="acct",
            user="user",
            password="secret",
            database="DB",
            schema="PUBLIC",
            warehouse="WH",
            stage="STAGE",
            table="TBL",
            stage_prefix="imednet/dev",
            batch_size=200,
            idempotent=False,
        ),
    )


def test_cli_export_snowflake_missing_dependency(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str) -> object | None:
        if name == "snowflake.connector":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = runner.invoke(
        cli.app,
        ["export", "snowflake", "STUDY", "acct", "user", "secret", "DB", "PUBLIC", "WH", "S", "T"],
    )

    assert result.exit_code == 1
    assert "imednet[snowflake]" in result.stdout
