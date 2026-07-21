"""Unit tests for csv injection."""

from pathlib import Path
from unittest.mock import MagicMock

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
        except Exception:
            import traceback

            err.write(traceback.format_exc())
            exit_code = 1

        # We also need to catch argparse sys.exit(2)
        return Result(exit_code, out.getvalue(), err.getvalue())


import imednet.cli as cli


@pytest.fixture
def runner() -> CliRunner:
    """Helper function to runner."""
    return CliRunner()


@pytest.fixture
def sdk(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Helper function to sdk."""
    mock_sdk = MagicMock()
    monkeypatch.setattr("imednet.cli.utils.context.get_sdk", MagicMock(return_value=mock_sdk))
    return mock_sdk


def test_records_list_output_csv_injection_prevention(
    runner: CliRunner, sdk: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that records list output csv injection prevention."""
    rec = MagicMock()
    # Malicious payload and normal payload
    rec.model_dump.return_value = {"recordId": 1, "note": "=cmd|' /C calc'!A0", "normal": "hello"}
    sdk.records.list.return_value = [rec]

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli.app, ["records", "list", "STUDY", "--output", "csv"])
    assert result.exit_code == 0

    with open("records.csv", encoding="utf-8") as f:
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
