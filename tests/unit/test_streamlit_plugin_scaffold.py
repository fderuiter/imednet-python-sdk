"""Unit tests for streamlit plugin scaffold."""

from __future__ import annotations

import importlib.util
import re
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "packages" / "plugins-streamlit"
PACKAGE_ROOT = PLUGIN_ROOT / "src" / "imednet_streamlit"
_MISSING = object()


def _component_palette() -> list[str]:
    """Helper function to  component palette."""
    return runpy.run_path(str(PACKAGE_ROOT / "components" / "charts.py"))["PALETTE"]


class _FakeNavigation:
    """Test suite for  FakeNavigation."""

    def __init__(self, pages: list[dict[str, Any]]) -> None:
        """Initialize the test object."""
        self.pages = pages
        self.ran = False

    def run(self) -> None:
        """Helper function to run."""
        self.ran = True


class _FakeSidebar:
    """Test suite for  FakeSidebar."""

    def toggle(self, label: str, value: bool = False, on_change: Any = None, **kwargs: Any) -> bool:
        """Helper function to toggle."""
        return value


class _FakeStreamlit:
    """Test suite for  FakeStreamlit."""

    def __init__(self) -> None:
        """Initialize the test object."""
        self.page_config: dict[str, Any] | None = None
        self.navigation_calls: list[_FakeNavigation] = []
        self.session_state: dict[str, Any] = {}
        self.query_params: dict[str, str] = {}
        self.sidebar = _FakeSidebar()

    def set_page_config(self, **kwargs: Any) -> None:
        """Helper function to set page config."""
        self.page_config = kwargs

    def page(
        self,
        path: str,
        *,
        title: str,
        icon: str,
        default: bool = False,
    ) -> dict[str, Any]:
        """Helper function to page."""
        return {
            "path": path,
            "title": title,
            "icon": icon,
            "default": default,
        }

    def navigation(self, pages: list[dict[str, Any]]) -> _FakeNavigation:
        """Helper function to navigation."""
        nav = _FakeNavigation(pages)
        self.navigation_calls.append(nav)
        return nav

    def markdown(self, body: str, **kwargs: Any) -> None:
        """Helper function to markdown."""
        pass

    def altair_chart(self, chart: Any, **kwargs: Any) -> None:
        """Helper function to altair chart."""
        pass

    def error(self, body: Any, *args: Any, **kwargs: Any) -> None:
        """Helper function to error."""
        pass

    def exception(self, exception: Any, *args: Any, **kwargs: Any) -> None:
        """Helper function to exception."""
        pass

    def warning(self, body: Any, *args: Any, **kwargs: Any) -> None:
        """Helper function to warning."""
        pass

    def info(self, body: Any, *args: Any, **kwargs: Any) -> None:
        """Helper function to info."""
        pass

    def expander(self, label: str, **kwargs: Any) -> _FakeContextManager:
        """Helper function to expander."""
        return _FakeContextManager()

    def dataframe(self, data: Any, **kwargs: Any) -> None:
        """Helper function to dataframe."""
        pass


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


class _FakeContextManager:
    """A no-op context manager (used for st.sidebar and column objects)."""

    def __enter__(self) -> "_FakeContextManager":
        """Helper function to   enter  ."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Helper function to   exit  ."""
        pass


class _FakeCacheDataDecorator:
    """Fake st.cache_data — identity decorator, clear() is a no-op."""

    def __call__(self, func: Any = None, **kwargs: Any) -> Any:
        """Helper function to   call  ."""
        if func is not None:
            return func
        return lambda f: f

    def clear(self) -> None:
        """Helper function to clear."""
        pass


class _FakeDashboardStreamlit(_FakePageStreamlit):
    """Extended fake Streamlit for dashboard pages with charts, filters, and exports."""

    def __init__(self, *, connected: bool) -> None:
        """Initialize the test object."""
        super().__init__(connected=connected)
        self.cache_data = _FakeCacheDataDecorator()
        self.sidebar = _FakeContextManager()
        self.warnings: list[str] = []
        self.subheaders: list[str] = []
        self.altair_charts: list[Any] = []
        self.dataframes: list[Any] = []
        self.download_calls: list[dict[str, Any]] = []
        self.metric_calls: list[dict[str, Any]] = []
        self.multiselect_values: dict[str, list[Any]] = {}

    # stubs that return sensible defaults so the page runs end-to-end
    def button(self, label: str, **kwargs: Any) -> bool:
        """Helper function to button."""
        return False

    def warning(self, value: str, **kwargs: Any) -> None:
        """Helper function to warning."""
        self.warnings.append(value)

    def subheader(self, value: str, **kwargs: Any) -> None:
        """Helper function to subheader."""
        self.subheaders.append(value)

    def altair_chart(self, chart: Any, **kwargs: Any) -> None:
        """Helper function to altair chart."""
        self.altair_charts.append(chart)

    def columns(self, spec: Any) -> list[Any]:
        """Helper function to columns."""
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def multiselect(self, label: str, options: Any, **kwargs: Any) -> list[Any]:
        """Helper function to multiselect."""
        if label in self.multiselect_values:
            return self.multiselect_values[label]
        return list(kwargs.get("default", []))

    def date_input(self, label: str, **kwargs: Any) -> list[Any]:
        """Helper function to date input."""
        val = kwargs.get("value", [])
        return list(val) if hasattr(val, "__iter__") else []

    def rerun(self) -> None:
        """Helper function to rerun."""
        pass

    def text_input(self, label: str, **kwargs: Any) -> str:
        """Helper function to text input."""
        return ""

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        """Helper function to dataframe."""
        self.dataframes.append(df)

    def download_button(self, **kwargs: Any) -> None:
        """Helper function to download button."""
        self.download_calls.append(kwargs)

    def metric(self, **kwargs: Any) -> None:
        """Helper function to metric."""
        self.metric_calls.append(kwargs)


def _make_fake_components_module(fake_st: _FakeDashboardStreamlit) -> ModuleType:
    """Build a fake components module so dashboard pages can be tested in isolation."""
    mod = ModuleType("imednet_streamlit.components")
    mod.PALETTE = _component_palette()  # type: ignore[attr-defined]

    def _noop_kpi_row(metrics: list[dict[str, Any]]) -> None:
        """Helper function to  noop kpi row."""
        fake_st.metric_calls.extend(metrics)

    def _noop_bar_chart(df: pd.DataFrame, **kwargs: Any) -> SimpleNamespace:
        """Helper function to  noop bar chart."""
        return SimpleNamespace(data=df.copy(), kwargs=kwargs)

    def _noop_line_chart(df: pd.DataFrame, **kwargs: Any) -> SimpleNamespace:
        """Helper function to  noop line chart."""
        return SimpleNamespace(data=df.copy(), kwargs=kwargs)

    def _noop_filterable_dataframe(df: pd.DataFrame, **kwargs: Any) -> None:
        """Helper function to  noop filterable dataframe."""
        fake_st.dataframes.append(df.copy())

    def _noop_csv_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        """Helper function to  noop csv download button."""
        fake_st.download_calls.append({"kind": "csv", "df": df.copy(), **kwargs})

    def _noop_excel_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        """Helper function to  noop excel download button."""
        fake_st.download_calls.append({"kind": "excel", "df": df.copy(), **kwargs})

    def _noop_top_n_with_other(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Helper function to  noop top n with other."""
        return df

    def _noop_paginated_slice(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Helper function to  noop paginated slice."""
        return df

    mod.kpi_row = _noop_kpi_row  # type: ignore[attr-defined]
    mod.bar_chart = _noop_bar_chart  # type: ignore[attr-defined]
    mod.line_chart = _noop_line_chart  # type: ignore[attr-defined]
    mod.filterable_dataframe = _noop_filterable_dataframe  # type: ignore[attr-defined]
    mod.csv_download_button = _noop_csv_download_button  # type: ignore[attr-defined]
    mod.excel_download_button = _noop_excel_download_button  # type: ignore[attr-defined]
    mod.top_n_with_other = _noop_top_n_with_other  # type: ignore[attr-defined]
    mod.paginated_slice = _noop_paginated_slice  # type: ignore[attr-defined]
    return mod


def _run_queries_page() -> _FakeDashboardStreamlit:
    """Execute queries.py with a comprehensive set of mocked dependencies."""
    page_path = PACKAGE_ROOT / "pages" / "queries.py"
    fake_st = _FakeDashboardStreamlit(connected=True)

    # Fake streamlit module
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "info",
        "success",
        "markdown",
        "warning",
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
    mock_sdk.get_queries.return_value = []
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    # Fake components module (avoids needing real altair/streamlit rendering)
    fake_components_module = _make_fake_components_module(fake_st)
    package_module = sys.modules.get("imednet_streamlit")
    saved_auth_attr = getattr(package_module, "auth", _MISSING) if package_module else _MISSING
    saved_components_attr = (
        getattr(package_module, "components", _MISSING) if package_module else _MISSING
    )

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
            "imednet_streamlit.components.charts",
            "imednet_workflows.query_management",
        )
    }

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        fake_charts = ModuleType("imednet_streamlit.components.charts")
        fake_charts.render_accessible_chart = lambda chart, *args, **kwargs: fake_st.altair_charts.append(chart)  # type: ignore[attr-defined]
        sys.modules["imednet_streamlit.components.charts"] = fake_charts
        sys.modules["imednet_workflows.query_management"] = fake_qm_module
        if package_module is not None:
            package_module.auth = fake_auth_module
            package_module.components = fake_components_module
        import importlib.util

        page_module_name = str(page_path).split("pages/")[-1].replace(".py", "")
        spec = importlib.util.spec_from_file_location(
            f"imednet_streamlit.pages.{page_module_name}", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"imednet_streamlit.pages.{page_module_name}"] = mod
        spec.loader.exec_module(mod)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original
        if package_module is not None:
            if saved_auth_attr is _MISSING:
                delattr(package_module, "auth")
            else:
                package_module.auth = saved_auth_attr
            if saved_components_attr is _MISSING:
                delattr(package_module, "components")
            else:
                package_module.components = saved_components_attr

    return fake_st


def _run_sites_page(
    *,
    subjects: list[Any] | None = None,
    open_queries: list[Any] | None = None,
) -> tuple[_FakeDashboardStreamlit, dict[str, Any]]:
    """Execute sites.py with mocked dependencies and capture Streamlit output."""
    page_path = PACKAGE_ROOT / "pages" / "sites.py"
    fake_st = _FakeDashboardStreamlit(connected=True)

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "info",
        "success",
        "markdown",
        "warning",
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

    mock_sdk = MagicMock()
    mock_sdk.get_subjects.return_value = subjects or []
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    fake_components_module = _make_fake_components_module(fake_st)
    package_module = sys.modules.get("imednet_streamlit")
    saved_auth_attr = getattr(package_module, "auth", _MISSING) if package_module else _MISSING
    saved_components_attr = (
        getattr(package_module, "components", _MISSING) if package_module else _MISSING
    )
    mock_workflow_cls = MagicMock()
    mock_workflow_instance = MagicMock()
    mock_workflow_instance.get_open_queries.return_value = open_queries or []
    mock_workflow_cls.return_value = mock_workflow_instance

    fake_qm_module = ModuleType("imednet_workflows.query_management")
    fake_qm_module.QueryManagementWorkflow = mock_workflow_cls  # type: ignore[attr-defined]
    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
            "imednet_streamlit.components.charts",
            "imednet_workflows.query_management",
        )
    }

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        fake_charts = ModuleType("imednet_streamlit.components.charts")
        fake_charts.render_accessible_chart = lambda chart, *args, **kwargs: fake_st.altair_charts.append(chart)  # type: ignore[attr-defined]
        sys.modules["imednet_streamlit.components.charts"] = fake_charts
        if package_module is not None:
            package_module.auth = fake_auth_module
            package_module.components = fake_components_module
        sys.modules["imednet_workflows.query_management"] = fake_qm_module
        import importlib.util

        page_module_name = str(page_path).split("pages/")[-1].replace(".py", "")
        spec = importlib.util.spec_from_file_location(
            f"imednet_streamlit.pages.{page_module_name}", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"imednet_streamlit.pages.{page_module_name}"] = mod
        spec.loader.exec_module(mod)
        module_globals = mod.__dict__
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original
        if package_module is not None:
            if saved_auth_attr is _MISSING:
                delattr(package_module, "auth")
            else:
                package_module.auth = saved_auth_attr
            if saved_components_attr is _MISSING:
                delattr(package_module, "components")
            else:
                package_module.components = saved_components_attr

    return fake_st, module_globals


def _run_records_page(
    *,
    records: list[Any] | None = None,
    forms: list[Any] | None = None,
    multiselect_values: dict[str, list[Any]] | None = None,
) -> tuple[_FakeDashboardStreamlit, dict[str, Any]]:
    """Execute records.py with mocked dependencies and capture the module namespace."""
    page_path = PACKAGE_ROOT / "pages" / "records.py"
    fake_st = _FakeDashboardStreamlit(connected=True)
    fake_st.multiselect_values = multiselect_values or {}

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "info",
        "success",
        "markdown",
        "warning",
        "button",
        "subheader",
        "altair_chart",
        "columns",
        "multiselect",
        "rerun",
        "text_input",
        "dataframe",
        "download_button",
        "metric",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))
    fake_streamlit_module.cache_data = fake_st.cache_data  # type: ignore[attr-defined]
    fake_streamlit_module.sidebar = fake_st.sidebar  # type: ignore[attr-defined]

    mock_sdk = MagicMock()
    mock_sdk.get_records.return_value = records or []
    mock_sdk.get_forms.return_value = forms or []
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    fake_components_module = _make_fake_components_module(fake_st)
    package_module = sys.modules.get("imednet_streamlit")
    saved_auth_attr = getattr(package_module, "auth", _MISSING) if package_module else _MISSING
    saved_components_attr = (
        getattr(package_module, "components", _MISSING) if package_module else _MISSING
    )

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
            "imednet_streamlit.components.charts",
        )
    }

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        fake_charts = ModuleType("imednet_streamlit.components.charts")
        fake_charts.render_accessible_chart = lambda chart, *args, **kwargs: fake_st.altair_charts.append(chart)  # type: ignore[attr-defined]
        sys.modules["imednet_streamlit.components.charts"] = fake_charts
        if package_module is not None:
            package_module.auth = fake_auth_module
            package_module.components = fake_components_module
        import importlib.util

        page_module_name = str(page_path).split("pages/")[-1].replace(".py", "")
        spec = importlib.util.spec_from_file_location(
            f"imednet_streamlit.pages.{page_module_name}", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"imednet_streamlit.pages.{page_module_name}"] = mod
        spec.loader.exec_module(mod)
        module_globals = mod.__dict__
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original
        if package_module is not None:
            if saved_auth_attr is _MISSING:
                delattr(package_module, "auth")
            else:
                package_module.auth = saved_auth_attr
            if saved_components_attr is _MISSING:
                delattr(package_module, "components")
            else:
                package_module.components = saved_components_attr

    return fake_st, module_globals


def _expected_version() -> str:
    """Helper function to  expected version."""
    pyproject_text = (PLUGIN_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, re.MULTILINE)
    assert version_match is not None
    return version_match.group(1)


def _run_app(is_connected: bool) -> _FakeStreamlit:
    """Helper function to  run app."""
    app_path = PACKAGE_ROOT / "app.py"
    fake_st = _FakeStreamlit()
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.set_page_config = fake_st.set_page_config
    fake_streamlit_module.Page = fake_st.page
    fake_streamlit_module.navigation = fake_st.navigation
    fake_streamlit_module.session_state = fake_st.session_state
    fake_streamlit_module.query_params = fake_st.query_params
    fake_streamlit_module.sidebar = fake_st.sidebar
    fake_streamlit_module.markdown = fake_st.markdown
    fake_streamlit_module.altair_chart = fake_st.altair_chart
    fake_streamlit_module.error = fake_st.error
    fake_streamlit_module.exception = fake_st.exception
    fake_streamlit_module.warning = fake_st.warning
    fake_streamlit_module.info = fake_st.info
    fake_streamlit_module.expander = fake_st.expander
    fake_streamlit_module.dataframe = fake_st.dataframe

    fake_auth_module = ModuleType("imednet_streamlit.auth")

    def _render_auth_sidebar() -> bool:
        """Helper function to  render auth sidebar."""
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
    """Helper function to  run page."""
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
        import importlib.util

        page_module_name = str(page_path).split("pages/")[-1].replace(".py", "")
        spec = importlib.util.spec_from_file_location(
            f"imednet_streamlit.pages.{page_module_name}", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"imednet_streamlit.pages.{page_module_name}"] = mod
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


def test_streamlit_plugin_version() -> None:
    """Test that streamlit plugin version."""
    init_path = PACKAGE_ROOT / "__init__.py"
    package_spec = importlib.util.spec_from_file_location(
        "imednet_streamlit", init_path, submodule_search_locations=[str(PACKAGE_ROOT)]
    )
    assert package_spec is not None and package_spec.loader is not None
    package_module = importlib.util.module_from_spec(package_spec)
    package_spec.loader.exec_module(package_module)

    assert package_module.__version__ == _expected_version()


def test_streamlit_app_navigation_is_home_only_before_auth() -> None:
    """Test that streamlit app navigation is home only before auth."""
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
    assert [page["path"] for page in nav.pages] == [
        "pages/home.py",
        "pages/admin.py",
        "pages/conformance.py",
    ]


def test_streamlit_app_navigation_includes_all_pages_after_auth() -> None:
    """Test that streamlit app navigation includes all pages after auth."""
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
        "pages/setup_wizard.py",
        "pages/review_workbench.py",
        "pages/publisher_wizard.py",
        "pages/data_lineage.py",
        "pages/admin.py",
        "pages/conformance.py",
    ]


def test_streamlit_pages_scaffold_exists() -> None:
    """Test that streamlit pages scaffold exists."""
    pages_root = PACKAGE_ROOT / "pages"

    assert (pages_root / "__init__.py").is_file()
    assert (pages_root / "home.py").is_file()
    assert (pages_root / "queries.py").is_file()
    assert (pages_root / "enrollment.py").is_file()
    assert (pages_root / "sites.py").is_file()
    assert (pages_root / "records.py").is_file()
    assert (pages_root / "setup_wizard.py").is_file()
    assert (pages_root / "review_workbench.py").is_file()
    assert (pages_root / "publisher_wizard.py").is_file()
    assert (pages_root / "data_lineage.py").is_file()


def test_streamlit_pages_execute_without_exceptions() -> None:
    """Test that streamlit pages execute without exceptions."""
    home_disconnected = _run_page("home.py", connected=False)
    assert "🏥 iMednet EDC Dashboard" in home_disconnected.titles
    assert home_disconnected.infos

    home_connected = _run_page("home.py", connected=True)
    assert any("Connected to study:" in m for m in home_connected.markdowns)


def test_queries_page_renders() -> None:
    """queries.py should render title and not raise, even with an empty dataset."""
    fake_st = _run_queries_page()
    assert "🔍 Query Status Overview" in fake_st.titles


def test_sites_page_renders() -> None:
    """sites.py should render metrics, charts, and exports for site data."""
    subjects = [
        SimpleNamespace(subject_key="SUBJ-001", site_name="Site A", deleted=False),
        SimpleNamespace(subject_key="SUBJ-002", site_name="Site A", deleted=False),
        SimpleNamespace(subject_key="SUBJ-003", site_name="Site B", deleted=False),
    ]
    open_queries = [
        SimpleNamespace(
            subject_key="SUBJ-001",
            annotation_id=101,
            date_created="2026-01-01T00:00:00Z",
        ),
        SimpleNamespace(
            subject_key="SUBJ-003",
            annotation_id=102,
            date_created="2026-01-02T00:00:00Z",
        ),
    ]
    fake_st, _ = _run_sites_page(subjects=subjects, open_queries=open_queries)

    assert "🏥 Site Performance" in fake_st.titles
    assert fake_st.metric_calls == [
        {"label": "Total Sites", "value": 2},
        {"label": "Total Enrolled", "value": 3},
        {"label": "Total Open Queries", "value": 2},
        {"label": "Avg Query Rate %", "value": "66.7%"},
    ]
    assert len(fake_st.altair_charts) == 2
    assert len(fake_st.dataframes) == 1
    assert len(fake_st.download_calls) == 1
    assert fake_st.download_calls[0]["filename"] == "site_metrics.csv"
    assert fake_st.download_calls[0]["df"]["site_name"].tolist() == ["Site A", "Site B"]
    assert fake_st.download_calls[0]["df"]["query_rate"].tolist() == [50.0, 100.0]


def test_records_page_renders_with_filtered_metrics_and_downloads() -> None:
    """Test that records page renders with filtered metrics and downloads."""
    records = [
        SimpleNamespace(
            record_id=1,
            form_key="AE",
            subject_key="SUBJ-001",
            site_id=1,
            record_status="Incomplete",
            record_type="CRF",
            deleted=False,
            date_created="2026-01-01",
            date_modified="2026-01-02",
        ),
        SimpleNamespace(
            record_id=2,
            form_key="AE",
            subject_key="SUBJ-002",
            site_id=1,
            record_status="Verified",
            record_type="CRF",
            deleted=False,
            date_created="2026-01-03",
            date_modified="2026-01-04",
        ),
        SimpleNamespace(
            record_id=3,
            form_key="LAB",
            subject_key="SUBJ-003",
            site_id=2,
            record_status="Complete",
            record_type="CRF",
            deleted=False,
            date_created="2026-01-05",
            date_modified="2026-01-06",
        ),
        SimpleNamespace(
            record_id=4,
            form_key="AE",
            subject_key="SUBJ-004",
            site_id=1,
            record_status="Complete",
            record_type="CRF",
            deleted=True,
            date_created="2026-01-07",
            date_modified="2026-01-08",
        ),
    ]
    forms = [
        SimpleNamespace(form_key="AE", form_name="Adverse Events"),
        SimpleNamespace(form_key="LAB", form_name="Laboratory Results"),
    ]

    fake_st, _ = _run_records_page(
        records=records,
        forms=forms,
        multiselect_values={
            "Form": ["Adverse Events"],
            "Site": ["1"],
            "Status": ["Incomplete", "Verified"],
        },
    )

    assert "📋 Data Completeness" in fake_st.titles
    assert fake_st.metric_calls == [
        {"label": "Total Records", "value": 2},
        {"label": "Complete", "value": 0},
        {"label": "Incomplete", "value": 1},
        {"label": "Pending SDV", "value": 0},
        {"label": "Verified", "value": 1},
    ]
    assert len(fake_st.altair_charts) == 3
    assert len(fake_st.dataframes) == 1
    rendered_df = fake_st.dataframes[0]
    assert rendered_df["form_name"].tolist() == ["Adverse Events", "Adverse Events"]
    assert rendered_df["record_status"].tolist() == ["Incomplete", "Verified"]
    assert len(fake_st.download_calls) == 2


def test_records_fetch_and_heatmap_helpers_handle_deleted_records_and_caps() -> None:
    """Test that records fetch and heatmap helpers handle deleted records and caps."""
    _, records_globals = _run_records_page()
    fetch_records = records_globals["_fetch_records"]
    build_heatmap_source = records_globals["_build_heatmap_source"]
    apply_filters = records_globals["_apply_filters"]
    prepare_records_dataframe = records_globals["_prepare_records_dataframe"]

    mock_sdk = MagicMock()
    mock_sdk.get_records.return_value = [
        SimpleNamespace(
            record_id=1,
            form_key="AE",
            subject_key="SUBJ-001",
            site_id=1,
            record_status="Incomplete",
            record_type="CRF",
            deleted=False,
            date_created="2026-01-01",
            date_modified="2026-01-02",
        ),
        SimpleNamespace(
            record_id=2,
            form_key="AE",
            subject_key="SUBJ-002",
            site_id=1,
            record_status="Complete",
            record_type="CRF",
            deleted=True,
            date_created="2026-01-03",
            date_modified="2026-01-04",
        ),
    ]

    records_df = fetch_records(mock_sdk, "STUDY")
    forms_df = pd.DataFrame(
        [
            {"form_key": "AE", "form_name": "Adverse Events"},
            {"form_key": "LAB", "form_name": "Laboratory Results"},
        ]
    )
    merged_df = prepare_records_dataframe(records_df, forms_df)
    filtered_df = apply_filters(
        merged_df,
        form_filter=["Adverse Events"],
        site_filter=["1"],
        status_filter=["Incomplete"],
    )

    assert records_df["record_id"].tolist() == [1]
    assert filtered_df["subject_key"].tolist() == ["SUBJ-001"]

    heatmap_input = pd.DataFrame(
        [
            {
                "subject_key": f"SUBJ-{subject_index:03d}",
                "form_name": f"Form {form_index:02d}",
                "record_status": "Complete",
            }
            for subject_index in range(1, 52)
            for form_index in range(1, 22)
        ]
    )
    heatmap_df = build_heatmap_source(heatmap_input)

    assert heatmap_df["subject_key"].nunique() == 50
    assert heatmap_df["form_name"].nunique() == 20
    assert len(heatmap_df) == 1000


def test_records_page_warns_for_large_datasets() -> None:
    """Test that records page warns for large datasets."""
    large_records = [
        SimpleNamespace(
            record_id=index,
            form_key="AE",
            subject_key=f"SUBJ-{index:05d}",
            site_id=1,
            record_status="Incomplete",
            record_type="CRF",
            deleted=False,
            date_created="2026-01-01",
            date_modified="2026-01-02",
        )
        for index in range(1, 10_002)
    ]
    forms = [SimpleNamespace(form_key="AE", form_name="Adverse Events")]

    fake_st, _ = _run_records_page(records=large_records, forms=forms)

    assert len(fake_st.warnings) == 1
    assert "10,001 records" in fake_st.warnings[0]


def _run_enrollment_page() -> _FakeDashboardStreamlit:
    """Execute enrollment.py with a comprehensive set of mocked dependencies."""
    import datetime

    page_path = PACKAGE_ROOT / "pages" / "enrollment.py"
    fake_st = _FakeDashboardStreamlit(connected=True)

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

    def _make_subject(
        subject_id: int,
        subject_status: str,
        site_name: str,
        enrollment_start_date: datetime.datetime | None = None,
    ) -> MagicMock:
        """Helper function to  make subject."""
        s = MagicMock()
        s.subject_id = subject_id
        s.subject_key = f"S{subject_id:03d}"
        s.subject_status = subject_status
        s.site_id = 1
        s.site_name = site_name
        s.enrollment_start_date = enrollment_start_date
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
    mock_sdk.get_subjects.return_value = mock_subjects
    mock_sdk.get_sites.return_value = [mock_site]

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    fake_components_module = _make_fake_components_module(fake_st)
    fake_components_module.pie_chart = lambda df, **kw: SimpleNamespace(  # type: ignore[attr-defined]
        data=df.copy(), kwargs=kw
    )
    package_module = sys.modules.get("imednet_streamlit")
    saved_auth_attr = getattr(package_module, "auth", _MISSING) if package_module else _MISSING
    saved_components_attr = (
        getattr(package_module, "components", _MISSING) if package_module else _MISSING
    )

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
            "imednet_streamlit.components.charts",
        )
    }

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        fake_charts = ModuleType("imednet_streamlit.components.charts")
        fake_charts.render_accessible_chart = lambda chart, *args, **kwargs: fake_st.altair_charts.append(chart)  # type: ignore[attr-defined]
        sys.modules["imednet_streamlit.components.charts"] = fake_charts
        if package_module is not None:
            package_module.auth = fake_auth_module
            package_module.components = fake_components_module
        import importlib.util

        page_module_name = str(page_path).split("pages/")[-1].replace(".py", "")
        spec = importlib.util.spec_from_file_location(
            f"imednet_streamlit.pages.{page_module_name}", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"imednet_streamlit.pages.{page_module_name}"] = mod
        spec.loader.exec_module(mod)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original
        if package_module is not None:
            if saved_auth_attr is _MISSING:
                delattr(package_module, "auth")
            else:
                package_module.auth = saved_auth_attr
            if saved_components_attr is _MISSING:
                delattr(package_module, "components")
            else:
                package_module.components = saved_components_attr

    return fake_st


def test_enrollment_page_renders() -> None:
    """enrollment.py should render title and not raise, even with a minimal dataset."""
    fake_st = _run_enrollment_page()
    assert "👥 Subject Enrollment Overview" in fake_st.titles


def test_streamlit_plugin_has_py_typed_marker() -> None:
    """Test that streamlit plugin has py typed marker."""
    py_typed = PACKAGE_ROOT / "py.typed"
    assert py_typed.is_file()
