from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


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


def _run_app(is_connected: bool) -> _FakeStreamlit:
    app_path = PACKAGE_ROOT / "app.py"
    fake_st = _FakeStreamlit()
    fake_streamlit_module: Any = ModuleType("streamlit")
    fake_streamlit_module.set_page_config = fake_st.set_page_config
    fake_streamlit_module.Page = fake_st.page
    fake_streamlit_module.navigation = fake_st.navigation

    fake_auth_module: Any = ModuleType("imednet_streamlit.auth")

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
        "pages/reporting_dashboard.py",
        "pages/sites.py",
        "pages/records.py",
    ]
