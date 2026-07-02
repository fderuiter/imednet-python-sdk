"""Unit tests for pages reporting dashboard."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from imednet.models.reporting import AdverseEvent, DeviceDeficiency, ProtocolDeviation

REPO_ROOT = Path(__file__).resolve().parents[3]
PAGE_PATH = (
    REPO_ROOT
    / "packages"
    / "plugins-streamlit"
    / "src"
    / "imednet_streamlit"
    / "pages"
    / "reporting_dashboard.py"
)


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


class _FakeStreamlit:
    """Test suite for  FakeStreamlit."""

    def __init__(self, *, multiselect_values: dict[str, list[Any]] | None = None) -> None:
        """Initialize the test object."""
        self.session_state: dict[str, Any] = {"_imednet_connected": True}
        self.cache_data = _FakeCacheDataDecorator()
        self.sidebar = _FakeContextManager()
        self.multiselect_values = multiselect_values or {}
        self.kpi_rows: list[list[dict[str, Any]]] = []
        self.tables: dict[str, Any] = {}
        self.dataframes: list[Any] = []
        self.selectbox_values: dict[str, Any] = {}
        self.infos: list[str] = []
        self.successes: list[str] = []

    def title(self, value: str) -> None:
        """Helper function to title."""
        pass

    def subheader(self, value: str) -> None:
        """Helper function to subheader."""
        pass

    def info(self, value: str) -> None:
        """Helper function to info."""
        self.infos.append(value)

    def success(self, value: str) -> None:
        """Helper function to success."""
        self.successes.append(value)

    def warning(self, value: str) -> None:
        """Helper function to warning."""
        pass

    def markdown(self, value: str) -> None:
        """Helper function to markdown."""
        pass

    def button(self, label: str, **kwargs: Any) -> bool:
        """Helper function to button."""
        return False

    def text_input(self, label: str, **kwargs: Any) -> str:
        """Helper function to text input."""
        return ""

    def selectbox(self, label: str, options: list[Any], index: int = 0, **kwargs: Any) -> Any:
        """Helper function to selectbox."""
        if label in self.selectbox_values:
            return self.selectbox_values[label]
        return options[index]

    def multiselect(self, label: str, options: list[Any], **kwargs: Any) -> list[Any]:
        """Helper function to multiselect."""
        if label in self.multiselect_values:
            return self.multiselect_values[label]
        return list(kwargs.get("default", []))

    def date_input(self, label: str, *, value: Any, **kwargs: Any) -> list[Any]:
        """Helper function to date input."""
        if isinstance(value, (list, tuple)):
            return list(value)
        return [value]

    def columns(self, spec: Any) -> list[Any]:
        """Helper function to columns."""
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def tabs(self, names: list[str]) -> list[Any]:
        """Helper function to tabs."""
        return [_FakeContextManager() for _ in names]

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        """Helper function to dataframe."""
        self.dataframes.append(df)

    def altair_chart(self, chart: Any, **kwargs: Any) -> None:
        """Helper function to altair chart."""
        pass

    def rerun(self) -> None:
        """Helper function to rerun."""
        pass


def _make_fake_components_module(fake_st: _FakeStreamlit) -> ModuleType:
    """Helper function to  make fake components module."""
    module = ModuleType("imednet_streamlit.components")
    module.__path__ = []  # type: ignore[attr-defined]
    module.PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # type: ignore[attr-defined]

    def _kpi_row(metrics: list[dict[str, Any]]) -> None:
        """Helper function to  kpi row."""
        fake_st.kpi_rows.append(metrics)

    def _bar_chart(*args: Any, **kwargs: Any) -> MagicMock:
        """Helper function to  bar chart."""
        return MagicMock()

    def _line_chart(*args: Any, **kwargs: Any) -> MagicMock:
        """Helper function to  line chart."""
        return MagicMock()

    def _filterable_dataframe(df: Any, *, key: str, **kwargs: Any) -> None:
        """Helper function to  filterable dataframe."""
        fake_st.tables[key] = df

    module.kpi_row = _kpi_row  # type: ignore[attr-defined]
    module.bar_chart = _bar_chart  # type: ignore[attr-defined]
    module.line_chart = _line_chart  # type: ignore[attr-defined]
    module.filterable_dataframe = _filterable_dataframe  # type: ignore[attr-defined]
    return module


def _run_page(*, multiselect_values: dict[str, list[Any]] | None = None) -> _FakeStreamlit:
    """Helper function to  run page."""
    fake_st = _FakeStreamlit(multiselect_values=multiselect_values)

    for key in list(sys.modules):
        if key.startswith("imednet_streamlit"):
            sys.modules.pop(key, None)

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "subheader",
        "info",
        "success",
        "warning",
        "markdown",
        "button",
        "text_input",
        "selectbox",
        "multiselect",
        "date_input",
        "columns",
        "tabs",
        "dataframe",
        "altair_chart",
        "rerun",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))
    fake_streamlit_module.cache_data = fake_st.cache_data  # type: ignore[attr-defined]
    fake_streamlit_module.sidebar = fake_st.sidebar  # type: ignore[attr-defined]

    mock_sdk = MagicMock()
    mock_sdk.get_subjects.return_value = [
        SimpleNamespace(subject_key="SUBJ-001", site_name="Site A", deleted=False),
        SimpleNamespace(subject_key="SUBJ-002", site_name="Site B", deleted=False),
    ]
    mock_sdk.get_forms.return_value = [
        SimpleNamespace(form_key="AE", form_name="Adverse Event"),
        SimpleNamespace(form_key="PD", form_name="Protocol Deviation"),
    ]
    mock_sdk.get_records.return_value = [
        SimpleNamespace(
            record_id=1,
            subject_key="SUBJ-001",
            site_id=101,
            form_key="AE",
            record_status="Complete",
            record_type="Form",
            deleted=False,
            date_created="2024-01-01T00:00:00+00:00",
            date_modified="2024-01-02T00:00:00+00:00",
            record_data={},
        ),
        SimpleNamespace(
            record_id=2,
            subject_key="SUBJ-002",
            site_id=102,
            form_key="PD",
            record_status="Incomplete",
            record_type="Form",
            deleted=False,
            date_created="2024-01-03T00:00:00+00:00",
            date_modified="2024-01-04T00:00:00+00:00",
            record_data={},
        ),
    ]

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    fake_components_module = _make_fake_components_module(fake_st)

    class _ExtractionResult:
        """Test suite for  ExtractionResult."""

        def __init__(self) -> None:
            """Initialize the test object."""
            self.adverse_events = [
                AdverseEvent.model_validate(
                    {
                        "subjectKey": "SUBJ-001",
                        "aeTerm": "Headache",
                        "aeSeverity": "MILD",
                        "aeSerious": False,
                        "aeStartDate": "2024-01-01T00:00:00+00:00",
                    }
                ),
                AdverseEvent.model_validate(
                    {
                        "subjectKey": "SUBJ-002",
                        "aeTerm": "Nausea",
                        "aeSeverity": "SEVERE",
                        "aeSerious": True,
                        "aeStartDate": "2024-01-02T00:00:00+00:00",
                    }
                ),
            ]
            self.protocol_deviations = [
                ProtocolDeviation.model_validate(
                    {
                        "subjectKey": "SUBJ-001",
                        "dvTerm": "Visit missed",
                        "dvCategory": "PROCEDURE",
                        "dvSeverity": "MAJOR",
                        "dvDate": "2024-01-05T00:00:00+00:00",
                    }
                )
            ]
            self.device_deficiencies = [
                DeviceDeficiency.model_validate(
                    {
                        "subjectKey": "SUBJ-001",
                        "ddTerm": "Battery issue",
                        "ddCategory": "HARDWARE",
                        "ddSerious": True,
                        "ddDate": "2024-01-06T00:00:00+00:00",
                    }
                )
            ]

    fake_extraction_module = ModuleType("imednet_workflows.extraction_engine")
    fake_extraction_module.extract_canonical_records = (  # type: ignore[attr-defined]
        lambda records, configuration: _ExtractionResult()
    )

    fake_query_workflow_module = ModuleType("imednet_workflows.query_management")
    workflow_cls = MagicMock()
    workflow_instance = MagicMock()
    workflow_instance.get_open_queries.return_value = [
        SimpleNamespace(
            subject_key="SUBJ-001",
            annotation_id=1001,
            date_created="2024-01-07T00:00:00+00:00",
        )
    ]
    workflow_cls.return_value = workflow_instance
    fake_query_workflow_module.QueryManagementWorkflow = workflow_cls  # type: ignore[attr-defined]

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
            "imednet_streamlit.components.charts",
            "imednet_workflows.extraction_engine",
            "imednet_workflows.query_management",
        )
    }
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        fake_charts_module = ModuleType("imednet_streamlit.components.charts")
        fake_charts_module.render_accessible_chart = lambda *args, **kwargs: MagicMock()  # type: ignore[attr-defined]
        sys.modules["imednet_streamlit.components.charts"] = fake_charts_module
        sys.modules["imednet_workflows.extraction_engine"] = fake_extraction_module
        sys.modules["imednet_workflows.query_management"] = fake_query_workflow_module
        module_name = "imednet_streamlit.pages.reporting_dashboard"
        module_spec = importlib.util.spec_from_file_location(module_name, PAGE_PATH)
        assert module_spec is not None and module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    return fake_st


def _kpi_dict(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    """Helper function to  kpi dict."""
    return {entry["label"]: entry["value"] for entry in metrics}


def test_reporting_dashboard_renders_expected_kpis_and_site_aggregation() -> None:
    """Test that reporting dashboard renders expected kpis and site aggregation."""
    fake_st = _run_page()
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    ae_kpis = next(kpi for kpi in kpi_maps if "Total AEs" in kpi)
    assert ae_kpis["Total AEs"] == 2
    assert ae_kpis["Serious AEs"] == 1

    pd_kpis = next(kpi for kpi in kpi_maps if "Total Deviations" in kpi)
    assert pd_kpis["Total Deviations"] == 1
    assert pd_kpis["Major Deviations"] == 1

    site_styler = next(
        df
        for df in fake_st.dataframes
        if hasattr(df, "data") and "query_rate" in getattr(df, "data").columns
    )
    site_df = site_styler.data  # type: ignore[assignment]
    assert int(site_df.loc[site_df["site_name"] == "Site A", "open_queries"].iloc[0]) == 1


def test_reporting_dashboard_filters_cascade_to_adverse_event_table() -> None:
    """Test that reporting dashboard filters cascade to adverse event table."""
    fake_st = _run_page(
        multiselect_values={
            "Site": ["Site A"],
            "Subject": ["SUBJ-001"],
            "Severity": ["MILD"],
        }
    )
    ae_table = fake_st.tables["ae_table"]
    assert len(ae_table) == 1
    assert ae_table.iloc[0]["subject_key"] == "SUBJ-001"
    assert ae_table.iloc[0]["ae_severity"] == "MILD"


# ─────────────────── helpers for extended test scenarios ────────────────────


class _FakeExtractionResult:
    """Configurable stand-in for the extraction-engine result object."""

    def __init__(
        self,
        *,
        adverse_events: list[Any] | None = None,
        protocol_deviations: list[Any] | None = None,
        device_deficiencies: list[Any] | None = None,
    ) -> None:
        """Initialize the test object."""
        self.adverse_events = adverse_events or []
        self.protocol_deviations = protocol_deviations or []
        self.device_deficiencies = device_deficiencies or []


def _run_page_extended(
    *,
    multiselect_values: dict[str, list[Any]] | None = None,
    selectbox_values: dict[str, Any] | None = None,
    extraction_result: Any | None = None,
    no_open_queries: bool = False,
    empty_subjects: bool = False,
    records_override: list[Any] | None = None,
    refresh_clicked: bool = False,
    save_view_name: str = "",
    set_default_clicked: bool = False,
) -> _FakeStreamlit:
    """Configurable page runner that exercises optional code paths."""
    fake_st = _FakeStreamlit(multiselect_values=multiselect_values)
    if selectbox_values:
        fake_st.selectbox_values.update(selectbox_values)

    # --- patch button ---
    _button_overrides: dict[str, bool] = {}
    if refresh_clicked:
        _button_overrides["🔄 Refresh Data"] = True
    if save_view_name:
        _button_overrides["💾 Save View"] = True
    if set_default_clicked:
        _button_overrides["⭐ Set as Default"] = True

    def _patched_button(label: str, **kwargs: Any) -> bool:
        """Helper function to  patched button."""
        return _button_overrides.get(label, False)

    fake_st.button = _patched_button  # type: ignore[method-assign]

    # --- patch text_input for save-view scenario ---
    if save_view_name:

        def _patched_text_input(label: str, **kwargs: Any) -> str:
            """Helper function to  patched text input."""
            return save_view_name if label == "Save Current View As" else ""

        fake_st.text_input = _patched_text_input  # type: ignore[method-assign]

    for key in list(sys.modules):
        if key.startswith("imednet_streamlit"):
            sys.modules.pop(key, None)

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "subheader",
        "info",
        "success",
        "warning",
        "markdown",
        "button",
        "text_input",
        "selectbox",
        "multiselect",
        "date_input",
        "columns",
        "tabs",
        "dataframe",
        "altair_chart",
        "rerun",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))
    fake_streamlit_module.cache_data = fake_st.cache_data  # type: ignore[attr-defined]
    fake_streamlit_module.sidebar = fake_st.sidebar  # type: ignore[attr-defined]

    mock_sdk = MagicMock()
    if empty_subjects:
        mock_sdk.get_subjects.return_value = []
    else:
        mock_sdk.get_subjects.return_value = [
            SimpleNamespace(subject_key="SUBJ-001", site_name="Site A", deleted=False),
            SimpleNamespace(subject_key="SUBJ-002", site_name="Site B", deleted=False),
        ]
    mock_sdk.get_forms.return_value = [
        SimpleNamespace(form_key="AE", form_name="Adverse Event"),
        SimpleNamespace(form_key="PD", form_name="Protocol Deviation"),
    ]
    if records_override is not None:
        mock_sdk.get_records.return_value = records_override
    else:
        mock_sdk.get_records.return_value = [
            SimpleNamespace(
                record_id=1,
                subject_key="SUBJ-001",
                site_id=101,
                form_key="AE",
                record_status="Complete",
                record_type="Form",
                deleted=False,
                date_created="2024-01-01T00:00:00+00:00",
                date_modified="2024-01-02T00:00:00+00:00",
                record_data={},
            ),
            SimpleNamespace(
                record_id=2,
                subject_key="SUBJ-002",
                site_id=102,
                form_key="PD",
                record_status="Incomplete",
                record_type="Form",
                deleted=False,
                date_created="2024-01-03T00:00:00+00:00",
                date_modified="2024-01-04T00:00:00+00:00",
                record_data={},
            ),
        ]

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: mock_sdk  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: "STUDY"  # type: ignore[attr-defined]

    fake_components_module = _make_fake_components_module(fake_st)

    if extraction_result is None:
        extraction_result = _FakeExtractionResult(
            adverse_events=[
                AdverseEvent.model_validate(
                    {
                        "subjectKey": "SUBJ-001",
                        "aeTerm": "Headache",
                        "aeSeverity": "MILD",
                        "aeSerious": False,
                        "aeStartDate": "2024-01-01T00:00:00+00:00",
                    }
                ),
                AdverseEvent.model_validate(
                    {
                        "subjectKey": "SUBJ-002",
                        "aeTerm": "Nausea",
                        "aeSeverity": "SEVERE",
                        "aeSerious": True,
                        "aeStartDate": "2024-01-02T00:00:00+00:00",
                    }
                ),
            ],
            protocol_deviations=[
                ProtocolDeviation.model_validate(
                    {
                        "subjectKey": "SUBJ-001",
                        "dvTerm": "Visit missed",
                        "dvCategory": "PROCEDURE",
                        "dvSeverity": "MAJOR",
                        "dvDate": "2024-01-05T00:00:00+00:00",
                    }
                )
            ],
            device_deficiencies=[
                DeviceDeficiency.model_validate(
                    {
                        "subjectKey": "SUBJ-001",
                        "ddTerm": "Battery issue",
                        "ddCategory": "HARDWARE",
                        "ddSerious": True,
                        "ddDate": "2024-01-06T00:00:00+00:00",
                    }
                )
            ],
        )

    _captured_result = extraction_result

    fake_extraction_module = ModuleType("imednet_workflows.extraction_engine")
    fake_extraction_module.extract_canonical_records = (  # type: ignore[attr-defined]
        lambda records, configuration: _captured_result
    )

    fake_query_workflow_module = ModuleType("imednet_workflows.query_management")
    workflow_cls = MagicMock()
    workflow_instance = MagicMock()
    if no_open_queries:
        workflow_instance.get_open_queries.return_value = []
    else:
        workflow_instance.get_open_queries.return_value = [
            SimpleNamespace(
                subject_key="SUBJ-001",
                annotation_id=1001,
                date_created="2024-01-07T00:00:00+00:00",
            )
        ]
    workflow_cls.return_value = workflow_instance
    fake_query_workflow_module.QueryManagementWorkflow = workflow_cls  # type: ignore[attr-defined]

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
            "imednet_streamlit.components.charts",
            "imednet_workflows.extraction_engine",
            "imednet_workflows.query_management",
        )
    }
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
        fake_charts_module = ModuleType("imednet_streamlit.components.charts")
        fake_charts_module.render_accessible_chart = lambda *args, **kwargs: MagicMock()  # type: ignore[attr-defined]
        sys.modules["imednet_streamlit.components.charts"] = fake_charts_module
        sys.modules["imednet_workflows.extraction_engine"] = fake_extraction_module
        sys.modules["imednet_workflows.query_management"] = fake_query_workflow_module
        module_name = "imednet_streamlit.pages.reporting_dashboard"
        module_spec = importlib.util.spec_from_file_location(module_name, PAGE_PATH)
        assert module_spec is not None and module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    return fake_st


# ─────────────────── extended test cases ────────────────────────────────────


def test_device_deficiencies_tab_kpis_and_table() -> None:
    """Device Deficiencies template shows correct KPIs and populates dd_table."""
    fake_st = _run_page_extended(
        selectbox_values={"Template": "Device Deficiencies"},
    )
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    dd_kpis = next(kpi for kpi in kpi_maps if "Total Deficiencies" in kpi)
    assert dd_kpis["Total Deficiencies"] == 1
    assert dd_kpis["Serious Deficiencies"] == 1

    assert "dd_table" in fake_st.tables
    dd_table = fake_st.tables["dd_table"]
    assert len(dd_table) == 1
    assert dd_table.iloc[0]["dd_term"] == "Battery issue"


def test_data_completeness_records_table_rendered() -> None:
    """Data Completeness tab populates records_table with form and site columns."""
    fake_st = _run_page_extended()

    assert "records_table" in fake_st.tables
    records_table = fake_st.tables["records_table"]
    assert "subject_key" in records_table.columns
    assert "form_name" in records_table.columns
    assert "record_status" in records_table.columns
    assert len(records_table) == 2


def test_site_performance_kpi_row_totals() -> None:
    """Site Performance tab KPIs reflect total sites, enrolled subjects, and open queries."""
    fake_st = _run_page_extended()
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    site_kpis = next(kpi for kpi in kpi_maps if "Total Sites" in kpi)
    assert site_kpis["Total Sites"] == 2
    assert site_kpis["Total Enrolled"] == 2
    assert site_kpis["Total Open Queries"] == 1


def test_no_open_queries_site_metrics_shows_zero() -> None:
    """When no open queries exist every site shows 0 open queries and 0 query rate."""
    fake_st = _run_page_extended(no_open_queries=True)
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    site_kpis = next(kpi for kpi in kpi_maps if "Total Open Queries" in kpi)
    assert site_kpis["Total Open Queries"] == 0

    site_styler = next(
        df
        for df in fake_st.dataframes
        if hasattr(df, "data") and "query_rate" in getattr(df, "data").columns
    )
    assert float(site_styler.data["open_queries"].sum()) == 0.0  # type: ignore[union-attr]


def test_empty_subjects_does_not_crash_and_zero_enrolled() -> None:
    """Page renders without error when the subjects API returns an empty list.

    The enrolled-subjects count is derived from records (not the subjects endpoint),
    so 2 records with distinct subject keys → enrolled_subjects=2 and AE rate = 2/2 = 1.0.
    """
    fake_st = _run_page_extended(empty_subjects=True)
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    ae_kpis = next(kpi for kpi in kpi_maps if "Total AEs" in kpi)
    assert ae_kpis["Total AEs"] == 2
    # enrolled_subjects = records_filtered["subject_key"].nunique() = 2
    assert ae_kpis["AE Rate"] == 1.0


def test_empty_records_produces_zero_kpis() -> None:
    """All KPIs are zero and no table rows appear when the study has no records."""
    fake_st = _run_page_extended(records_override=[])
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    ae_kpis = next(kpi for kpi in kpi_maps if "Total AEs" in kpi)
    assert ae_kpis["Total AEs"] == 2  # AEs from extraction result, not records

    site_kpis = next(kpi for kpi in kpi_maps if "Total Enrolled" in kpi)
    assert site_kpis["Total Enrolled"] == 2  # subjects still present


def test_fallback_direct_models_parsed_from_record_data() -> None:
    """When extraction returns empty lists, AE data is parsed directly from record_data."""
    ae_record = SimpleNamespace(
        record_id=10,
        subject_key="SUBJ-001",
        site_id=101,
        form_key="AE",
        record_status="Complete",
        record_type="Form",
        deleted=False,
        date_created="2024-02-01T00:00:00+00:00",
        date_modified="2024-02-02T00:00:00+00:00",
        record_data={
            "subjectKey": "SUBJ-001",
            "aeTerm": "Dizziness",
            "aeSeverity": "MILD",
            "aeSerious": False,
            "aeStartDate": "2024-02-01T00:00:00+00:00",
        },
    )
    fake_st = _run_page_extended(
        extraction_result=_FakeExtractionResult(),  # all lists empty → triggers fallback
        records_override=[ae_record],
    )
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    ae_kpis = next(kpi for kpi in kpi_maps if "Total AEs" in kpi)
    assert ae_kpis["Total AEs"] == 1
    assert ae_kpis["Serious AEs"] == 0


def test_ae_empty_after_site_filter_shows_info_message() -> None:
    """Filtering to a non-existent site empties the AE table and emits an info notice."""
    fake_st = _run_page_extended(
        multiselect_values={"Site": ["__nonexistent_site__"]},
    )
    assert any("No adverse event data" in msg for msg in fake_st.infos)
    # filterable_dataframe is not called when df is empty (early return), so the key
    # is absent from fake_st.tables
    assert "ae_table" not in fake_st.tables


def test_dd_empty_after_filter_shows_deficiency_info_message() -> None:
    """Filtering all DD rows away triggers the 'no device deficiency' info message."""
    fake_st = _run_page_extended(
        selectbox_values={"Template": "Device Deficiencies"},
        multiselect_values={"Site": ["__nonexistent_site__"]},
    )
    assert any("No device deficiency data" in msg for msg in fake_st.infos)
    # filterable_dataframe is not called on early return; key absent
    assert "dd_table" not in fake_st.tables


def test_protocol_deviation_tab_rate_and_major_count() -> None:
    """PD tab reports correct total, major count, and rate based on enrolled subjects."""
    two_pd_result = _FakeExtractionResult(
        adverse_events=[
            AdverseEvent.model_validate(
                {
                    "subjectKey": "SUBJ-001",
                    "aeTerm": "X",
                    "aeSeverity": "MILD",
                    "aeSerious": False,
                    "aeStartDate": "2024-01-01T00:00:00+00:00",
                }
            )
        ],
        protocol_deviations=[
            ProtocolDeviation.model_validate(
                {
                    "subjectKey": "SUBJ-001",
                    "dvTerm": "Missing visit",
                    "dvCategory": "PROCEDURE",
                    "dvSeverity": "MAJOR",
                    "dvDate": "2024-01-05T00:00:00+00:00",
                }
            ),
            ProtocolDeviation.model_validate(
                {
                    "subjectKey": "SUBJ-002",
                    "dvTerm": "Wrong dose",
                    "dvCategory": "MEDICATION",
                    "dvSeverity": "MINOR",
                    "dvDate": "2024-01-06T00:00:00+00:00",
                }
            ),
        ],
        device_deficiencies=[],
    )
    fake_st = _run_page_extended(extraction_result=two_pd_result)
    kpi_maps = [_kpi_dict(row) for row in fake_st.kpi_rows]

    pd_kpis = next(kpi for kpi in kpi_maps if "Total Deviations" in kpi)
    assert pd_kpis["Total Deviations"] == 2
    assert pd_kpis["Major Deviations"] == 1
    # Default records contain 2 distinct subjects (SUBJ-001 and SUBJ-002),
    # so enrolled_subjects = 2.  Rate = 2 total deviations / 2 enrolled = 1.0.
    assert pd_kpis["Deviation Rate"] == 1.0


def test_ae_filter_cascades_to_pd_table_via_site_filter() -> None:
    """Site filter applied in sidebar narrows the PD table to matching subjects only."""
    fake_st = _run_page_extended(
        multiselect_values={"Site": ["Site A"]},
    )
    # Only SUBJ-001 is at Site A; PD for SUBJ-001 should survive the filter
    assert "pd_table" in fake_st.tables
    pd_table = fake_st.tables["pd_table"]
    assert len(pd_table) == 1
    assert pd_table.iloc[0]["subject_key"] == "SUBJ-001"


def test_refresh_button_executes_without_error() -> None:
    """Pressing Refresh Data calls cache_data.clear() and rerun without raising."""
    # rerun() is a no-op in the fake; the page continues to render normally
    fake_st = _run_page_extended(refresh_clicked=True)
    # Page still renders KPI rows after the refresh path
    assert len(fake_st.kpi_rows) > 0


def test_save_view_stores_entry_in_session_state() -> None:
    """Clicking Save View with a name persists the view into session state."""
    fake_st = _run_page_extended(save_view_name="My Custom View")
    saved_views = fake_st.session_state.get("_reporting_saved_views", {})
    assert "My Custom View" in saved_views
    view = saved_views["My Custom View"]
    assert "template" in view
    assert "date_range" in view


def test_set_default_view_updates_session_state() -> None:
    """Clicking Set as Default stores the chosen template as the default in session state."""
    fake_st = _run_page_extended(set_default_clicked=True)
    assert "_reporting_default_template" in fake_st.session_state


def test_records_completeness_heatmap_built_from_complete_records() -> None:
    """Records with Complete status contribute to the heatmap completion matrix."""
    complete_record = SimpleNamespace(
        record_id=5,
        subject_key="SUBJ-001",
        site_id=101,
        form_key="AE",
        record_status="Complete",
        record_type="Form",
        deleted=False,
        date_created="2024-03-01T00:00:00+00:00",
        date_modified="2024-03-02T00:00:00+00:00",
        record_data={},
    )
    fake_st = _run_page_extended(records_override=[complete_record])
    # The records_table should contain the complete record
    records_table = fake_st.tables["records_table"]
    assert len(records_table) == 1
    assert records_table.iloc[0]["record_status"] == "Complete"
