"""Unit tests for pages queries."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


class _FakeContextManager:
    """Test suite for  FakeContextManager."""

    def __enter__(self) -> "_FakeContextManager":
        """Helper function to   enter  ."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Helper function to   exit  ."""
        pass


class _FakeCacheDataDecorator:
    """Test suite for  FakeCacheDataDecorator."""

    def __call__(self, func: Any = None, **kwargs: Any) -> Any:
        """Helper function to   call  ."""
        if func is not None:
            return func
        return lambda f: f

    def clear(self) -> None:
        """Helper function to clear."""
        pass


class _FakeQueriesStreamlit:
    """Test suite for  FakeQueriesStreamlit."""

    def __init__(self) -> None:
        """Initialize the test object."""
        self.session_state: dict[str, Any] = {"_imednet_connected": True}
        self.titles: list[str] = []
        self.infos: list[str] = []
        self.successes: list[str] = []
        self.markdowns: list[str] = []
        self.cache_data = _FakeCacheDataDecorator()
        self.sidebar = _FakeContextManager()

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

    def button(self, label: str, **kwargs: Any) -> bool:
        """Helper function to button."""
        return False

    def subheader(self, value: str, **kwargs: Any) -> None:
        """Helper function to subheader."""
        pass

    def altair_chart(self, chart: Any, **kwargs: Any) -> None:
        """Helper function to altair chart."""
        pass

    def columns(self, spec: Any) -> list[Any]:
        """Helper function to columns."""
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def multiselect(self, label: str, options: Any, **kwargs: Any) -> list[Any]:
        """Helper function to multiselect."""
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
        pass

    def download_button(self, **kwargs: Any) -> None:
        """Helper function to download button."""
        pass

    def metric(self, **kwargs: Any) -> None:
        """Helper function to metric."""
        pass


def _make_fake_components_module() -> ModuleType:
    """Helper function to  make fake components module."""
    import pandas as pd

    mod = ModuleType("imednet_streamlit.components")
    mod.charts = ModuleType("imednet_streamlit.components.charts")
    mod.charts.render_accessible_chart = MagicMock()
    mod.render_accessible_chart = mod.charts.render_accessible_chart

    def _noop_kpi_row(metrics: list[dict[str, Any]]) -> None:
        """Helper function to  noop kpi row."""
        pass

    def _noop_bar_chart(df: pd.DataFrame, **kwargs: Any) -> MagicMock:
        """Helper function to  noop bar chart."""
        return MagicMock()

    def _noop_line_chart(df: pd.DataFrame, **kwargs: Any) -> MagicMock:
        """Helper function to  noop line chart."""
        return MagicMock()

    def _noop_filterable_dataframe(df: pd.DataFrame, **kwargs: Any) -> None:
        """Helper function to  noop filterable dataframe."""
        pass

    def _noop_csv_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        """Helper function to  noop csv download button."""
        pass

    def _noop_excel_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        """Helper function to  noop excel download button."""
        pass

    def _noop_top_n_with_other(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Helper function to  noop top n with other."""
        return df

    mod.kpi_row = _noop_kpi_row  # type: ignore[attr-defined]
    mod.bar_chart = _noop_bar_chart  # type: ignore[attr-defined]
    mod.line_chart = _noop_line_chart  # type: ignore[attr-defined]
    mod.filterable_dataframe = _noop_filterable_dataframe  # type: ignore[attr-defined]
    mod.csv_download_button = _noop_csv_download_button  # type: ignore[attr-defined]
    mod.excel_download_button = _noop_excel_download_button  # type: ignore[attr-defined]
    mod.top_n_with_other = _noop_top_n_with_other  # type: ignore[attr-defined]
    return mod


def test_queries_page_renders_with_mock_sdk() -> None:
    """Test that queries page renders with mock sdk."""
    page_path = PACKAGE_ROOT / "pages" / "queries.py"
    fake_st = _FakeQueriesStreamlit()

    # Clean up cached imednet_streamlit modules to avoid import-binding pollution
    for key in list(sys.modules.keys()):
        if key.startswith("imednet_streamlit"):
            sys.modules.pop(key, None)

    # Create mock streamlit module
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

    # Mock sdk
    mock_sdk = MagicMock()
    mock_sdk.get_queries.return_value = []

    # Mock auth module
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    # Mock components
    fake_components_module = _make_fake_components_module()

    # Mock workflows
    mock_workflow_cls = MagicMock()
    mock_workflow_instance = MagicMock()
    mock_workflow_instance.get_open_queries.return_value = []
    mock_workflow_cls.return_value = mock_workflow_instance

    fake_qm_module = ModuleType("imednet_workflows.query_management")
    fake_qm_module.QueryManagementWorkflow = mock_workflow_cls  # type: ignore[attr-defined]

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
        sys.modules["imednet_streamlit.components.charts"] = fake_components_module.charts
        sys.modules["imednet_workflows.query_management"] = fake_qm_module
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "imednet_streamlit.pages.queries", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["imednet_streamlit.pages.queries"] = mod
        spec.loader.exec_module(mod)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original

    assert "🔍 Query Status Overview" in fake_st.titles


def test_queries_page_populated_and_filters_and_refresh() -> None:
    """Test that queries page populated and filters and refresh."""
    page_path = PACKAGE_ROOT / "pages" / "queries.py"
    fake_st = _FakeQueriesStreamlit()

    # Stub button and multiselect
    def _button(label: str, **kwargs: Any) -> bool:
        """Helper function to  button."""
        if label == "🔄 Refresh Data":
            return True
        return False

    def _multiselect(label: str, options: Any, **kwargs: Any) -> list[Any]:
        """Helper function to  multiselect."""
        if label == "Annotation Type":
            return ["Missing"]
        return list(kwargs.get("default", []))

    fake_st.button = _button  # type: ignore[assignment]
    fake_st.multiselect = _multiselect  # type: ignore[assignment]

    # Clean up cached imednet_streamlit modules
    for key in list(sys.modules.keys()):
        if key.startswith("imednet_streamlit"):
            sys.modules.pop(key, None)

    # Create mock streamlit module
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

    # Mock sdk queries
    import datetime

    import pandas as pd

    mock_q = MagicMock()
    mock_q.annotation_id = 123
    mock_q.subject_key = "S001"
    mock_q.variable = "AGE"
    mock_q.annotation_type = "Missing"
    mock_q.description = "Age is missing"
    mock_q.date_created = pd.Timestamp(datetime.datetime(2024, 1, 10))
    mock_q.date_modified = pd.Timestamp(datetime.datetime(2024, 1, 11))

    mock_sdk = MagicMock()
    mock_sdk.get_queries.return_value = [mock_q]

    # Mock auth module
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    # Mock components
    fake_components_module = _make_fake_components_module()

    # Mock workflows
    mock_workflow_cls = MagicMock()
    mock_workflow_instance = MagicMock()
    mock_workflow_instance.get_open_queries.return_value = [mock_q]
    mock_workflow_cls.return_value = mock_workflow_instance

    fake_qm_module = ModuleType("imednet_workflows.query_management")
    fake_qm_module.QueryManagementWorkflow = mock_workflow_cls  # type: ignore[attr-defined]

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
        sys.modules["imednet_streamlit.components.charts"] = fake_components_module.charts
        sys.modules["imednet_workflows.query_management"] = fake_qm_module
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "imednet_streamlit.pages.queries", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["imednet_streamlit.pages.queries"] = mod
        spec.loader.exec_module(mod)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original

    assert "🔍 Query Status Overview" in fake_st.titles
