from __future__ import annotations

import sys
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch


def test_dashboard_missing_plugin() -> None:
    """When imednet_streamlit is not installed, exit code 1 with helpful message."""
    from importlib import import_module

    original_import_module = import_module

    def mock_import_module(name: str, package: str | None = None) -> Any:
        if name.startswith("imednet_streamlit"):
            raise ImportError(f"No module named '{name}'")
        return original_import_module(name, package)

    # Clean up sys.modules to ensure imednet.cli is imported fresh under this patch
    for key in list(sys.modules.keys()):
        if key.startswith("imednet.cli"):
            sys.modules.pop(key, None)

    with patch("importlib.import_module", side_effect=mock_import_module):
        from typer.testing import CliRunner

        from imednet.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["dashboard"])

    assert result.exit_code == 1
    assert "pip install imednet-streamlit" in result.output


def test_dashboard_launches_subprocess() -> None:
    """When plugin is installed, subprocess.run is called with correct args."""
    streamlit_mock = ModuleType("streamlit")
    mock_module = MagicMock()
    mock_module.__file__ = "/fake/path/app.py"

    from importlib import import_module

    original_import_module = import_module

    def mock_import_module(name: str, package: str | None = None) -> Any:
        if name.startswith("imednet_streamlit"):
            return mock_module
        return original_import_module(name, package)

    # Clean up sys.modules to ensure imednet.cli is imported fresh under this patch
    for key in list(sys.modules.keys()):
        if key.startswith("imednet.cli"):
            sys.modules.pop(key, None)

    with patch.dict("sys.modules", {"streamlit": streamlit_mock}):
        with patch("importlib.import_module", side_effect=mock_import_module):
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
