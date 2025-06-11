from click.testing import CliRunner
from imednet_py.cli import cli


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "0.1.0"
