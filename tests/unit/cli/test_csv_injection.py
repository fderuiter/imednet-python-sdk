from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

import imednet.cli as cli


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def sdk(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock_sdk = MagicMock()
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=mock_sdk))
    return mock_sdk


def test_records_list_output_csv_injection_prevention(runner: CliRunner, sdk: MagicMock) -> None:
    rec = MagicMock()
    # Malicious payload and normal payload
    rec.model_dump.return_value = {"recordId": 1, "note": "=cmd|' /C calc'!A0", "normal": "hello"}
    sdk.records.list.return_value = [rec]

    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "csv"])
        assert result.exit_code == 0

        with open("records.csv", "r", encoding="utf-8") as f:
            content = f.read()
            print(f"CSV Content: {content}")

            # The header shouldn't be touched
            assert "recordId,note,normal" in content or "recordId" in content

            # The malicious payload should be sanitized (prefixed with ')
            # We check that the RAW malicious string is NOT present as a starting value

            # Since we are using csv module, it might quote fields.
            # But the value inside quotes should not start with =

            # If sanitized, it should look like: ',"'=cmd...
            # If not sanitized: ',"=cmd...

            assert "'=cmd|' /C calc'!A0" in content
