from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "packages" / "plugins-streamlit"
PACKAGE_ROOT = PLUGIN_ROOT / "src" / "imednet_streamlit"


def _expected_version() -> str:
    pyproject_text = (PLUGIN_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, re.MULTILINE)
    assert version_match is not None
    return version_match.group(1)


def test_streamlit_plugin_version() -> None:
    init_path = PACKAGE_ROOT / "__init__.py"
    package_spec = importlib.util.spec_from_file_location(
        "imednet_streamlit", init_path, submodule_search_locations=[str(PACKAGE_ROOT)]
    )
    assert package_spec is not None and package_spec.loader is not None
    package_module = importlib.util.module_from_spec(package_spec)
    package_spec.loader.exec_module(package_module)

    assert package_module.__version__ == _expected_version()


def test_streamlit_plugin_app_import() -> None:
    app_path = PACKAGE_ROOT / "app.py"

    app_spec = importlib.util.spec_from_file_location("imednet_streamlit.app", app_path)
    assert app_spec is not None and app_spec.loader is not None
    app_module = importlib.util.module_from_spec(app_spec)
    app_spec.loader.exec_module(app_module)

    assert app_module.__file__ is not None
    assert Path(app_module.__file__).resolve() == app_path.resolve()
    app_source = app_path.read_text(encoding="utf-8")
    assert "Full implementation: see feat-2 (Base App Scaffold) issue." in app_source


def test_streamlit_plugin_has_py_typed_marker() -> None:
    py_typed = PACKAGE_ROOT / "py.typed"
    assert py_typed.is_file()
