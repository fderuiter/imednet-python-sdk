from __future__ import annotations

import sys
from pathlib import Path


def test_streamlit_plugin_version_and_app_import() -> None:
    package_src = Path(__file__).resolve().parents[2] / "packages" / "plugins-streamlit" / "src"
    sys.path.insert(0, str(package_src))
    try:
        import imednet_streamlit
        import imednet_streamlit.app

        assert imednet_streamlit.__version__ == "0.1.0"
        assert imednet_streamlit.app.__file__
    finally:
        sys.path.pop(0)


def test_streamlit_plugin_has_py_typed_marker() -> None:
    py_typed = (
        Path(__file__).resolve().parents[2]
        / "packages"
        / "plugins-streamlit"
        / "src"
        / "imednet_streamlit"
        / "py.typed"
    )
    assert py_typed.is_file()
