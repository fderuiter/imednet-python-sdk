from __future__ import annotations

import importlib.util
import re
import runpy
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

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


class _FakeContextManager:
    """A no-op context manager (used for st.sidebar and column objects)."""

    def __enter__(self) -> "_FakeContextManager":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class _FakeCacheDataDecorator:
    """Fake st.cache_data — identity decorator, clear() is a no-op."""

    def __call__(self, func: Any = None, **kwargs: Any) -> Any:
        if func is not None:
            return func
        return lambda f: f

    def clear(self) -> None:
        pass


class _FakeQueriesStreamlit(_FakePageStreamlit):
    """Extended fake Streamlit for the fully-implemented queries page."""

    def __init__(self, *, connected: bool) -> None:
        super().__init__(connected=connected)
        self.cache_data = _FakeCacheDataDecorator()
        self.sidebar = _FakeContextManager()

    # stubs that return sensible defaults so the page runs end-to-end
    def button(self, label: str, **kwargs: Any) -> bool:
        return False

    def subheader(self, value: str, **kwargs: Any) -> None:
        pass

    def altair_chart(self, chart: Any, **kwargs: Any) -> None:
        pass

    def columns(self, spec: Any) -> list[Any]:
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def multiselect(self, label: str, options: Any, **kwargs: Any) -> list[Any]:
        return list(kwargs.get("default", []))

    def date_input(self, label: str, **kwargs: Any) -> list[Any]:
        val = kwargs.get("value", [])
        return list(val) if hasattr(val, "__iter__") else []

    def rerun(self) -> None:
        pass

    def text_input(self, label: str, **kwargs: Any) -> str:
        return ""

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        pass

    def download_button(self, **kwargs: Any) -> None:
        pass

    def metric(self, **kwargs: Any) -> None:
        pass


def _make_fake_components_module() -> ModuleType:
    """Build a no-op components module so the queries page can be tested in isolation."""
    import pandas as pd

    mod = ModuleType("imednet_streamlit.components")

    def _noop_kpi_row(metrics: list[dict[str, Any]]) -> None:
        pass

    def _noop_bar_chart(df: pd.DataFrame, **kwargs: Any) -> MagicMock:
        return MagicMock()

    def _noop_line_chart(df: pd.DataFrame, **kwargs: Any) -> MagicMock:
        return MagicMock()

    def _noop_filterable_dataframe(df: pd.DataFrame, **kwargs: Any) -> None:
        pass

    def _noop_csv_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        pass

    def _noop_excel_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        pass

    mod.kpi_row = _noop_kpi_row  # type: ignore[attr-defined]
    mod.bar_chart = _noop_bar_chart  # type: ignore[attr-defined]
    mod.line_chart = _noop_line_chart  # type: ignore[attr-defined]
    mod.filterable_dataframe = _noop_filterable_dataframe  # type: ignore[attr-defined]
    mod.csv_download_button = _noop_csv_download_button  # type: ignore[attr-defined]
    mod.excel_download_button = _noop_excel_download_button  # type: ignore[attr-defined]
    return mod


def _run_queries_page() -> _FakeQueriesStreamlit:
    """Execute queries.py with a comprehensive set of mocked dependencies."""
    page_path = PACKAGE_ROOT / "pages" / "queries.py"
    fake_st = _FakeQueriesStreamlit(connected=True)

    # Fake streamlit module
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "info",
        "success",
        "markdown",
        "button",
        "subheader",
        "altair_chart",
        "columns",
        "multiselect",
        "date_input",
        "rerun",
        "text_input",
        "dataframe",
        "download_button",
        "metric",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))
    fake_streamlit_module.cache_data = fake_st.cache_data  # type: ignore[attr-defined]
    fake_streamlit_module.sidebar = fake_st.sidebar  # type: ignore[attr-defined]

    # Fake auth module
    mock_sdk = MagicMock()
    mock_sdk.queries.list.return_value = []
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    # Fake components module (avoids needing real altair/streamlit rendering)
    fake_components_module = _make_fake_components_module()

    # Fake imednet_workflows.query_management module
    mock_workflow_cls = MagicMock()
    mock_workflow_instance = MagicMock()
    mock_workflow_instance.get_open_queries.return_value = []
    mock_workflow_cls.return_value = mock_workflow_instance

    fake_qm_module = ModuleType("imednet_workflows.query_management")
    fake_qm_module.QueryManagementWorkflow = mock_workflow_cls  # type: ignore[attr-defined]

    # Preserve originals
    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
            "imednet_workflows.query_management",
        )
    }

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        sys.modules["imednet_workflows.query_management"] = fake_qm_module
        runpy.run_path(str(page_path), run_name="__main__")
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original

    return fake_st


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

    for page_name in ("sites.py", "records.py"):
        page_streamlit = _run_page(page_name, connected=True)
        assert page_streamlit.titles
        assert page_streamlit.infos == ["This page is under construction."]


def test_queries_page_renders() -> None:
    """queries.py should render title and not raise, even with an empty dataset."""
    fake_st = _run_queries_page()
    assert "🔍 Query Status Overview" in fake_st.titles


def _run_enrollment_page() -> _FakeQueriesStreamlit:
    """Execute enrollment.py with a comprehensive set of mocked dependencies."""
    import datetime

    page_path = PACKAGE_ROOT / "pages" / "enrollment.py"
    fake_st = _FakeQueriesStreamlit(connected=True)

    # Fake streamlit module
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "info",
        "success",
        "markdown",
        "button",
        "subheader",
        "altair_chart",
        "columns",
        "multiselect",
        "date_input",
        "rerun",
        "text_input",
        "dataframe",
        "download_button",
        "metric",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))
    fake_streamlit_module.cache_data = fake_st.cache_data  # type: ignore[attr-defined]
    fake_streamlit_module.sidebar = fake_st.sidebar  # type: ignore[attr-defined]

    # Build a minimal subject mock
    def _make_subject(
        subject_id: int,
        subject_status: str,
        site_name: str,
        enrolled_date: datetime.datetime | None = None,
    ) -> MagicMock:
        s = MagicMock()
        s.subject_id = subject_id
        s.subject_key = f"S{subject_id:03d}"
        s.subject_status = subject_status
        s.site_id = 1
        s.site_name = site_name
        s.enrollment_start_date = enrolled_date
        s.deleted = False
        return s

    mock_subjects = [
        _make_subject(1, "Enrolled", "Site A", datetime.datetime(2024, 1, 10)),
        _make_subject(2, "Screened", "Site B"),
        _make_subject(3, "Withdrawn", "Site A"),
    ]

    # Build a minimal site mock
    mock_site = MagicMock()
    mock_site.model_dump.return_value = {"site_name": "Site A", "site_enrollment_status": "Open"}

    mock_sdk = MagicMock()
    mock_sdk.subjects.list.return_value = mock_subjects
    mock_sdk.sites.list.return_value = [mock_site]

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    # Fake components module
    fake_components_module = _make_fake_components_module()

    # Add pie_chart stub (enrollment page uses it)
    fake_components_module.pie_chart = lambda df, **kw: MagicMock()  # type: ignore[attr-defined]

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
        )
    }

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        runpy.run_path(str(page_path), run_name="__main__")
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original

    return fake_st


def test_enrollment_page_renders() -> None:
    """enrollment.py should render title and not raise, even with a minimal dataset."""
    fake_st = _run_enrollment_page()
    assert "👥 Subject Enrollment Overview" in fake_st.titles


def test_streamlit_plugin_has_py_typed_marker() -> None:
    py_typed = PACKAGE_ROOT / "py.typed"
    assert py_typed.is_file()
