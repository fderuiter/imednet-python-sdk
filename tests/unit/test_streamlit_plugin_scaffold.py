from __future__ import annotations

import importlib.util
import re
import runpy
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "packages" / "plugins-streamlit"
PACKAGE_ROOT = PLUGIN_ROOT / "src" / "imednet_streamlit"


class _FakeNavigation:
    def __init__(self, pages: list[dict[str, Any]]) -> None:
        self.pages = pages
        self.ran = False

    def run(self) -> None:
        self.ran = True


class _FakeStreamlit:
    def __init__(self) -> None:
        self.page_config: dict[str, Any] | None = None
        self.navigation_calls: list[_FakeNavigation] = []

    def set_page_config(self, **kwargs: Any) -> None:
        self.page_config = kwargs

    def page(
        self,
        path: str,
        *,
        title: str,
        icon: str,
        default: bool = False,
    ) -> dict[str, Any]:
        return {
            "path": path,
            "title": title,
            "icon": icon,
            "default": default,
        }

    def navigation(self, pages: list[dict[str, Any]]) -> _FakeNavigation:
        nav = _FakeNavigation(pages)
        self.navigation_calls.append(nav)
        return nav


class _FakePageStreamlit:
    def __init__(self, *, connected: bool) -> None:
        self.session_state: dict[str, Any] = {"_imednet_connected": connected}
        self.titles: list[str] = []
        self.infos: list[str] = []
        self.successes: list[str] = []
        self.markdowns: list[str] = []

    def title(self, value: str) -> None:
        self.titles.append(value)

    def info(self, value: str) -> None:
        self.infos.append(value)

    def success(self, value: str) -> None:
        self.successes.append(value)

    def markdown(self, value: str) -> None:
        self.markdowns.append(value)


def _expected_version() -> str:
    pyproject_text = (PLUGIN_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, re.MULTILINE)
    assert version_match is not None
    return version_match.group(1)


def _run_app(is_connected: bool) -> _FakeStreamlit:
    app_path = PACKAGE_ROOT / "app.py"
    fake_st = _FakeStreamlit()
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.set_page_config = fake_st.set_page_config
    fake_streamlit_module.Page = fake_st.page
    fake_streamlit_module.navigation = fake_st.navigation

    fake_auth_module = ModuleType("imednet_streamlit.auth")

    def _render_auth_sidebar() -> bool:
        return is_connected

    fake_auth_module.render_auth_sidebar = _render_auth_sidebar

    previous_streamlit = sys.modules.get("streamlit")
    previous_auth = sys.modules.get("imednet_streamlit.auth")

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module

        app_spec = importlib.util.spec_from_file_location(
            f"imednet_streamlit.app_test_{int(is_connected)}", app_path
        )
        assert app_spec is not None and app_spec.loader is not None
        app_module = importlib.util.module_from_spec(app_spec)
        app_spec.loader.exec_module(app_module)
        assert app_module.__file__ is not None
        assert Path(app_module.__file__).resolve() == app_path.resolve()
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


def _run_page(page_name: str, *, connected: bool) -> _FakePageStreamlit:
    page_path = PACKAGE_ROOT / "pages" / page_name
    fake_st = _FakePageStreamlit(connected=connected)
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state
    fake_streamlit_module.title = fake_st.title
    fake_streamlit_module.info = fake_st.info
    fake_streamlit_module.success = fake_st.success
    fake_streamlit_module.markdown = fake_st.markdown

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: object()
    fake_auth_module.get_study_key = lambda: "STUDY"

    previous_streamlit = sys.modules.get("streamlit")
    previous_auth = sys.modules.get("imednet_streamlit.auth")
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        runpy.run_path(str(page_path), run_name="__main__")
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


def test_streamlit_plugin_version() -> None:
    init_path = PACKAGE_ROOT / "__init__.py"
    package_spec = importlib.util.spec_from_file_location(
        "imednet_streamlit", init_path, submodule_search_locations=[str(PACKAGE_ROOT)]
    )
    assert package_spec is not None and package_spec.loader is not None
    package_module = importlib.util.module_from_spec(package_spec)
    package_spec.loader.exec_module(package_module)

    assert package_module.__version__ == _expected_version()


def test_streamlit_app_navigation_is_home_only_before_auth() -> None:
    fake_st = _run_app(is_connected=False)

    assert fake_st.page_config == {
        "page_title": "iMednet EDC Dashboard",
        "page_icon": "🏥",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
    }
    assert len(fake_st.navigation_calls) == 1
    nav = fake_st.navigation_calls[0]
    assert nav.ran is True
    assert [page["path"] for page in nav.pages] == ["pages/home.py"]


def test_streamlit_app_navigation_includes_all_pages_after_auth() -> None:
    fake_st = _run_app(is_connected=True)

    assert len(fake_st.navigation_calls) == 1
    nav = fake_st.navigation_calls[0]
    assert nav.ran is True
    assert [page["path"] for page in nav.pages] == [
        "pages/home.py",
        "pages/queries.py",
        "pages/enrollment.py",
        "pages/sites.py",
        "pages/records.py",
    ]


def test_streamlit_pages_scaffold_exists() -> None:
    pages_root = PACKAGE_ROOT / "pages"

    assert (pages_root / "__init__.py").is_file()
    assert (pages_root / "home.py").is_file()
    assert (pages_root / "queries.py").is_file()
    assert (pages_root / "enrollment.py").is_file()
    assert (pages_root / "sites.py").is_file()
    assert (pages_root / "records.py").is_file()


def test_streamlit_pages_execute_without_exceptions() -> None:
    home_disconnected = _run_page("home.py", connected=False)
    assert "🏥 iMednet EDC Dashboard" in home_disconnected.titles
    assert home_disconnected.infos

    home_connected = _run_page("home.py", connected=True)
    assert home_connected.successes

    for page_name in ("queries.py", "enrollment.py", "sites.py", "records.py"):
        page_streamlit = _run_page(page_name, connected=True)
        assert page_streamlit.titles
        assert page_streamlit.infos == ["This page is under construction."]


def test_streamlit_plugin_has_py_typed_marker() -> None:
    py_typed = PACKAGE_ROOT / "py.typed"
    assert py_typed.is_file()
