"""TODO: Add docstring."""

from __future__ import annotations

import importlib
import importlib.util
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

FAKE_DASHBOARD_PATH = "/tmp/fake_dashboard.py"


@pytest.fixture()
def runner() -> CliRunner:
    """TODO: Add docstring."""
    return CliRunner()


@pytest.fixture()
def cli_module() -> ModuleType:
    """TODO: Add docstring."""
    import imednet.cli as cli

    importlib.reload(cli)
    yield cli
    importlib.reload(cli)


def test_dashboard_command_falls_back_when_plugin_missing(
    runner: CliRunner, cli_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO: Add docstring."""
    real_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str, package: str | None = None) -> object | None:
        """TODO: Add docstring."""
        if name in ("imednet_streamlit.app", "imednet_streamlit"):
            return None
        return real_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    reloaded_cli = importlib.reload(cli_module)

    help_result = runner.invoke(reloaded_cli.app, ["--help"])
    assert help_result.exit_code == 0
    assert "dashboard" in help_result.stdout

    result = runner.invoke(reloaded_cli.app, ["dashboard"])
    assert result.exit_code == 1
    assert "pip install imednet-streamlit" in result.stdout


def test_dashboard_command_runs_streamlit_when_plugin_present(
    runner: CliRunner, cli_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO: Add docstring."""
    real_find_spec = importlib.util.find_spec
    dashboard_spec = MagicMock(origin=FAKE_DASHBOARD_PATH)

    def fake_find_spec(name: str, package: str | None = None) -> object | None:
        """TODO: Add docstring."""
        if name in ("imednet_streamlit.app", "imednet_streamlit"):
            return dashboard_spec
        return real_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    reloaded_cli = importlib.reload(cli_module)
    mock_result = MagicMock(returncode=0)
    subprocess_run = MagicMock(return_value=mock_result)
    monkeypatch.setattr(reloaded_cli.subprocess, "run", subprocess_run)

    help_result = runner.invoke(reloaded_cli.app, ["dashboard", "--help"])
    assert help_result.exit_code == 0
    assert "Port to run the dashboard on." in help_result.stdout
    assert "Suppress automatic browser launch." in help_result.stdout

    result = runner.invoke(
        reloaded_cli.app, ["dashboard", "--port", "9999", "--no-browser"]
    )
    assert result.exit_code == 0
    assert "Launching iMednet Dashboard on port 9999..." in result.stdout
    subprocess_run.assert_called_once_with(
        [
            reloaded_cli.sys.executable,
            "-m",
            "streamlit",
            "run",
            FAKE_DASHBOARD_PATH,
            "--server.port",
            "9999",
            "--server.headless",
            "true",
        ],
        check=False,
    )


def test_dashboard_command_uses_default_options(
    runner: CliRunner, cli_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO: Add docstring."""
    real_find_spec = importlib.util.find_spec
    dashboard_spec = MagicMock(origin=FAKE_DASHBOARD_PATH)

    def fake_find_spec(name: str, package: str | None = None) -> object | None:
        """TODO: Add docstring."""
        if name in ("imednet_streamlit.app", "imednet_streamlit"):
            return dashboard_spec
        return real_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    reloaded_cli = importlib.reload(cli_module)
    mock_result = MagicMock(returncode=0)
    subprocess_run = MagicMock(return_value=mock_result)
    monkeypatch.setattr(reloaded_cli.subprocess, "run", subprocess_run)

    result = runner.invoke(reloaded_cli.app, ["dashboard"])
    assert result.exit_code == 0
    subprocess_run.assert_called_once_with(
        [
            reloaded_cli.sys.executable,
            "-m",
            "streamlit",
            "run",
            FAKE_DASHBOARD_PATH,
            "--server.port",
            "8501",
        ],
        check=False,
    )


def test_dashboard_command_fails_when_app_path_missing(
    runner: CliRunner, cli_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO: Add docstring."""
    real_find_spec = importlib.util.find_spec
    dashboard_spec = MagicMock(origin=None)

    def fake_find_spec(name: str, package: str | None = None) -> object | None:
        """TODO: Add docstring."""
        if name in ("imednet_streamlit.app", "imednet_streamlit"):
            return dashboard_spec
        return real_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    reloaded_cli = importlib.reload(cli_module)

    result = runner.invoke(reloaded_cli.app, ["dashboard"])
    assert result.exit_code == 1
    assert "Cannot resolve dashboard app path." in result.stdout


def test_dashboard_command_propagates_streamlit_failure(
    runner: CliRunner, cli_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO: Add docstring."""
    real_find_spec = importlib.util.find_spec
    dashboard_spec = MagicMock(origin=FAKE_DASHBOARD_PATH)

    def fake_find_spec(name: str, package: str | None = None) -> object | None:
        """TODO: Add docstring."""
        if name in ("imednet_streamlit.app", "imednet_streamlit"):
            return dashboard_spec
        return real_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    reloaded_cli = importlib.reload(cli_module)
    mock_result = MagicMock(returncode=7)
    subprocess_run = MagicMock(return_value=mock_result)
    monkeypatch.setattr(reloaded_cli.subprocess, "run", subprocess_run)

    result = runner.invoke(reloaded_cli.app, ["dashboard"])
    assert result.exit_code == 7
    assert "Dashboard failed to launch." in result.stdout


def test_dashboard_command_handles_subprocess_oserror(
    runner: CliRunner, cli_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO: Add docstring."""
    real_find_spec = importlib.util.find_spec
    dashboard_spec = MagicMock(origin=FAKE_DASHBOARD_PATH)

    def fake_find_spec(name: str, package: str | None = None) -> object | None:
        """TODO: Add docstring."""
        if name in ("imednet_streamlit.app", "imednet_streamlit"):
            return dashboard_spec
        return real_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    reloaded_cli = importlib.reload(cli_module)
    subprocess_run = MagicMock(side_effect=FileNotFoundError("streamlit not found"))
    monkeypatch.setattr(reloaded_cli.subprocess, "run", subprocess_run)

    result = runner.invoke(reloaded_cli.app, ["dashboard"])
    assert result.exit_code == 1
    assert "Dashboard failed to launch: streamlit not found" in result.stdout
