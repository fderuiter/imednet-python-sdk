from unittest.mock import MagicMock

import imednet.cli as cli
import pytest
from typer.testing import CliRunner


def test_decorator_handles_unexpected_error(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setenv("IMEDNET_API_KEY", "k")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "s")
    sdk = MagicMock()
    sdk.studies.list.side_effect = RuntimeError("boom")
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=sdk))

    result = runner.invoke(cli.app, ["studies", "list"])

    assert result.exit_code == 1
    assert "Unexpected error" in result.stdout
