"""TODO: Add docstring."""

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
    """TODO: Add docstring."""

    def __enter__(self) -> "_FakeContextManager":
        """TODO: Add docstring."""
        return self

    def __exit__(self, *args: Any) -> None:
        """TODO: Add docstring."""
        pass


class _FakeCacheDataDecorator:
    """TODO: Add docstring."""

    def __call__(self, func: Any = None, **kwargs: Any) -> Any:
        """TODO: Add docstring."""
        if func is not None:
            return func
        return lambda f: f

    def clear(self) -> None:
        """TODO: Add docstring."""
        pass


class _FakeQueriesStreamlit:
    """TODO: Add docstring."""

    def __init__(self) -> None:
        """TODO: Add docstring."""
        self.session_state: dict[str, Any] = {"_imednet_connected": True}
        self.titles: list[str] = []
        self.infos: list[str] = []
        self.successes: list[str] = []
        self.markdowns: list[str] = []
        self.cache_data = _FakeCacheDataDecorator()
        self.sidebar = _FakeContextManager()

    def title(self, value: str) -> None:
        """TODO: Add docstring."""
        self.titles.append(value)

    def info(self, value: str) -> None:
        """TODO: Add docstring."""
        self.infos.append(value)

    def success(self, value: str) -> None:
        """TODO: Add docstring."""
        self.successes.append(value)

    def markdown(self, value: str) -> None:
        """TODO: Add docstring."""
        self.markdowns.append(value)

    def button(self, label: str, **kwargs: Any) -> bool:
        """TODO: Add docstring."""
        return False

    def subheader(self, value: str, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def altair_chart(self, chart: Any, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def columns(self, spec: Any) -> list[Any]:
        """TODO: Add docstring."""
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def multiselect(self, label: str, options: Any, **kwargs: Any) -> list[Any]:
        """TODO: Add docstring."""
        return list(kwargs.get("default", []))

    def date_input(self, label: str, **kwargs: Any) -> list[Any]:
        """TODO: Add docstring."""
        val = kwargs.get("value", [])
        return list(val) if hasattr(val, "__iter__") else []

    def rerun(self) -> None:
        """TODO: Add docstring."""
        pass

    def text_input(self, label: str, **kwargs: Any) -> str:
        """TODO: Add docstring."""
        return ""

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def download_button(self, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def metric(self, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass


def _make_fake_components_module() -> ModuleType:
    """TODO: Add docstring."""
    import pandas as pd

    mod = ModuleType("imednet_streamlit.components")

    def _noop_kpi_row(metrics: list[dict[str, Any]]) -> None:
        """TODO: Add docstring."""
        pass

    def _noop_bar_chart(df: pd.DataFrame, **kwargs: Any) -> MagicMock:
        """TODO: Add docstring."""
        return MagicMock()

    def _noop_line_chart(df: pd.DataFrame, **kwargs: Any) -> MagicMock:
        """TODO: Add docstring."""
        return MagicMock()

    def _noop_filterable_dataframe(df: pd.DataFrame, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def _noop_csv_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def _noop_excel_download_button(df: pd.DataFrame, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def _noop_top_n_with_other(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """TODO: Add docstring."""
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
    """TODO: Add docstring."""
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
    """TODO: Add docstring."""
    page_path = PACKAGE_ROOT / "pages" / "queries.py"
    fake_st = _FakeQueriesStreamlit()

    # Stub button and multiselect
    def _button(label: str, **kwargs: Any) -> bool:
        """TODO: Add docstring."""
        if label == "🔄 Refresh Data":
            return True
        return False

    def _multiselect(label: str, options: Any, **kwargs: Any) -> list[Any]:
        """TODO: Add docstring."""
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
