"""Unit tests for pages enrollment."""

from __future__ import annotations

import datetime
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


class _FakeContextManager:
    """Test suite for  FakeContextManager."""

    def __enter__(self) -> _FakeContextManager:
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


class _FakeEnrollmentStreamlit:
    """Test suite for  FakeEnrollmentStreamlit."""

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

    def _noop_pie_chart(df: pd.DataFrame, **kwargs: Any) -> MagicMock:
        """Helper function to  noop pie chart."""
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

    mod.kpi_row = _noop_kpi_row  # type: ignore[attr-defined]
    mod.bar_chart = _noop_bar_chart  # type: ignore[attr-defined]
    mod.line_chart = _noop_line_chart  # type: ignore[attr-defined]
    mod.pie_chart = _noop_pie_chart  # type: ignore[attr-defined]
    mod.filterable_dataframe = _noop_filterable_dataframe  # type: ignore[attr-defined]
    mod.csv_download_button = _noop_csv_download_button  # type: ignore[attr-defined]
    mod.excel_download_button = _noop_excel_download_button  # type: ignore[attr-defined]
    return mod


def test_enrollment_page_renders_with_mock_sdk() -> None:
    """Test that enrollment page renders with mock sdk."""
    page_path = PACKAGE_ROOT / "pages" / "enrollment.py"
    fake_st = _FakeEnrollmentStreamlit()

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

    # Build a minimal subject mock
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

    # Mock auth module
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    # Mock components
    fake_components_module = _make_fake_components_module()

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
        sys.modules["imednet_streamlit.components.charts"] = fake_components_module.charts
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "imednet_streamlit.pages.enrollment", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["imednet_streamlit.pages.enrollment"] = mod
        spec.loader.exec_module(mod)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original

    assert "👥 Subject Enrollment Overview" in fake_st.titles


def test_enrollment_page_empty_and_filters_and_refresh() -> None:
    """Test that enrollment page empty and filters and refresh."""
    page_path = PACKAGE_ROOT / "pages" / "enrollment.py"
    fake_st = _FakeEnrollmentStreamlit()

    # Stub the button to return True for refresh, and multiselect to return filters
    def _button(label: str, **kwargs: Any) -> bool:
        """Helper function to  button."""
        return label == "🔄 Refresh Data"

    def _multiselect(label: str, options: Any, **kwargs: Any) -> list[Any]:
        """Helper function to  multiselect."""
        if label == "Site":
            return ["Site A"]
        if label == "Subject Status":
            return ["Enrolled"]
        return []

    fake_st.button = _button  # type: ignore[assignment]
    fake_st.multiselect = _multiselect  # type: ignore[assignment]

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

    # Build a minimal site mock
    mock_site = MagicMock()
    mock_site.model_dump.return_value = {"site_name": "Site A", "site_enrollment_status": "Open"}

    mock_sdk = MagicMock()
    mock_sdk.get_subjects.return_value = []
    mock_sdk.get_sites.return_value = [mock_site]

    # Mock auth module
    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    # Mock components
    fake_components_module = _make_fake_components_module()

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
        sys.modules["imednet_streamlit.components.charts"] = fake_components_module.charts

        # Execute page
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "imednet_streamlit.pages.enrollment", str(page_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["imednet_streamlit.pages.enrollment"] = mod
        spec.loader.exec_module(mod)

        # Now import and test _fetch_sites directly to cover lines 46-49
        from imednet_streamlit.pages.enrollment import _fetch_sites

        res = _fetch_sites(mock_sdk, "STUDY")
        assert len(res) == 1

        mock_sdk.get_sites.return_value = []
        res_empty = _fetch_sites(mock_sdk, "STUDY")
        assert res_empty.empty
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original
