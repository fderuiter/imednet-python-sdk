"""TODO: Add docstring."""
from __future__ import annotations

import sys
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch


def test_dashboard_missing_plugin() -> None:
    """When imednet_streamlit is not installed, exit code 1 with helpful message."""
    from importlib.util import find_spec

    original_find_spec = find_spec

    def mock_find_spec(name: str, package: str | None = None) -> Any:
        """TODO: Add docstring."""
        if name == "imednet_streamlit.app":
            return None
        return original_find_spec(name, package)

    with patch.dict(sys.modules, clear=False):
        for key in list(sys.modules.keys()):
            if key.startswith("imednet.cli"):
                sys.modules.pop(key, None)

        with patch("importlib.util.find_spec", side_effect=mock_find_spec):
            from typer.testing import CliRunner

            from imednet.cli import app

            runner = CliRunner()
            result = runner.invoke(app, ["dashboard"])

    assert result.exit_code == 1
    assert "pip install imednet-streamlit" in result.output


def test_dashboard_launches_subprocess() -> None:
    """When plugin is installed, subprocess.run is called with correct args."""
    streamlit_mock = ModuleType("streamlit")
    dashboard_spec = ModuleSpec("imednet_streamlit.app", loader=None, origin="/fake/path/app.py")

    from importlib.util import find_spec

    original_find_spec = find_spec

    def mock_find_spec(name: str, package: str | None = None) -> Any:
        """TODO: Add docstring."""
        if name == "imednet_streamlit.app":
            return dashboard_spec
        return original_find_spec(name, package)

    with patch.dict(sys.modules, clear=False):
        for key in list(sys.modules.keys()):
            if key.startswith("imednet.cli"):
                sys.modules.pop(key, None)
        sys.modules["streamlit"] = streamlit_mock

        with patch("importlib.util.find_spec", side_effect=mock_find_spec):
            from typer.testing import CliRunner

            from imednet.cli import app

            runner = CliRunner()
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = runner.invoke(app, ["dashboard", "--port", "9999", "--no-browser"])

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert "streamlit" in call_args
    assert "9999" in call_args
    assert "--server.headless" in call_args
    assert result.exit_code == 0
