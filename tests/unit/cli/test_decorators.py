from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

import imednet.cli as cli


def test_decorator_handles_unexpected_error(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")
    sdk = MagicMock()
    sdk.studies.list.side_effect = RuntimeError("boom")
    monkeypatch.setattr("imednet.cli.utils.context.get_sdk", MagicMock(return_value=sdk))

    result = runner.invoke(cli.app, ["studies", "list"])

    assert result.exit_code == 1
    assert "Unexpected error" in result.stdout
