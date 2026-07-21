"""Unit tests for pages home."""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import imednet_streamlit.pages  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


class _FakePageStreamlit:
    """Test suite for  FakePageStreamlit."""

    def __init__(self, *, connected: bool) -> None:
        """Initialize the test object."""
        self.session_state: dict[str, Any] = {"_imednet_connected": connected}
        self.titles: list[str] = []
        self.infos: list[str] = []
        self.successes: list[str] = []
        self.markdowns: list[str] = []

    def title(self, value: str) -> None:
        """Helper function to title."""
        self.titles.append(value)

    def info(self, value: str) -> None:
        """Helper function to info."""
        self.infos.append(value)

    def success(self, value: str) -> None:
        """Helper function to success."""
        self.successes.append(value)

    def markdown(self, value: str) -> None:
        """Helper function to markdown."""
        self.markdowns.append(value)


def _run_page(page_name: str, *, connected: bool) -> _FakePageStreamlit:
    """Helper function to  run page."""
    page_path = PACKAGE_ROOT / "pages" / page_name
    fake_st = _FakePageStreamlit(connected=connected)
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    fake_streamlit_module.title = fake_st.title  # type: ignore[attr-defined]
    fake_streamlit_module.info = fake_st.info  # type: ignore[attr-defined]
    fake_streamlit_module.success = fake_st.success  # type: ignore[attr-defined]
    fake_streamlit_module.markdown = fake_st.markdown  # type: ignore[attr-defined]

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: object()  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    previous_streamlit = sys.modules.get("streamlit")
    previous_auth = sys.modules.get("imednet_streamlit.auth")
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "imednet_streamlit.pages.home", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["imednet_streamlit.pages.home"] = mod
        spec.loader.exec_module(mod)
    finally:
        if previous_streamlit is None:
            sys.modules.pop("streamlit", None)
        else:
            sys.modules["streamlit"] = previous_streamlit
        if previous_auth is None:
            sys.modules.pop("imednet_streamlit.auth", None)
        else:
            sys.modules["imednet_streamlit.auth"] = previous_auth

    return fake_st


def test_home_page_renders_disconnected() -> None:
    """Test that home page renders disconnected."""
    home_disconnected = _run_page("home.py", connected=False)
    assert "🏥 iMednet EDC Dashboard" in home_disconnected.titles
    assert any("authenticate" in info.lower() for info in home_disconnected.infos)


def test_home_page_renders_connected() -> None:
    """Test that home page renders connected."""
    home_connected = _run_page("home.py", connected=True)
    assert any("connected" in md.lower() for md in home_connected.markdowns)
