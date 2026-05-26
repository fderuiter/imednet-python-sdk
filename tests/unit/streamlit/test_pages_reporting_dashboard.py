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
    def __enter__(self) -> "_FakeContextManager":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class _FakeCacheDataDecorator:
    def __call__(self, func: Any = None, **kwargs: Any) -> Any:
        if func is not None:
            return func
        return lambda f: f

    def clear(self) -> None:
        pass


class _FakeStreamlit:
    def __init__(self, *, multiselect_values: dict[str, list[Any]] | None = None) -> None:
        self.session_state: dict[str, Any] = {"_imednet_connected": True}
        self.cache_data = _FakeCacheDataDecorator()
        self.sidebar = _FakeContextManager()
        self.multiselect_values = multiselect_values or {}
        self.kpi_rows: list[list[dict[str, Any]]] = []
        self.tables: dict[str, Any] = {}
        self.dataframes: list[Any] = []
        self.selectbox_values: dict[str, Any] = {}

    def title(self, value: str) -> None:
        pass

    def subheader(self, value: str) -> None:
        pass

    def info(self, value: str) -> None:
        pass

    def success(self, value: str) -> None:
        pass

    def warning(self, value: str) -> None:
        pass

    def markdown(self, value: str) -> None:
        pass

    def button(self, label: str, **kwargs: Any) -> bool:
        return False

    def text_input(self, label: str, **kwargs: Any) -> str:
        return ""

    def selectbox(self, label: str, options: list[Any], index: int = 0, **kwargs: Any) -> Any:
        if label in self.selectbox_values:
            return self.selectbox_values[label]
        return options[index]

    def multiselect(self, label: str, options: list[Any], **kwargs: Any) -> list[Any]:
        if label in self.multiselect_values:
            return self.multiselect_values[label]
        return list(kwargs.get("default", []))

    def date_input(self, label: str, *, value: Any, **kwargs: Any) -> list[Any]:
        if isinstance(value, (list, tuple)):
            return list(value)
        return [value]

    def columns(self, spec: Any) -> list[Any]:
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def tabs(self, names: list[str]) -> list[Any]:
        return [_FakeContextManager() for _ in names]

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        self.dataframes.append(df)

    def altair_chart(self, chart: Any, **kwargs: Any) -> None:
        pass

    def rerun(self) -> None:
        pass


def _make_fake_components_module(fake_st: _FakeStreamlit) -> ModuleType:
    module = ModuleType("imednet_streamlit.components")
    module.PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # type: ignore[attr-defined]

    def _kpi_row(metrics: list[dict[str, Any]]) -> None:
        fake_st.kpi_rows.append(metrics)

    def _bar_chart(*args: Any, **kwargs: Any) -> MagicMock:
        return MagicMock()

    def _line_chart(*args: Any, **kwargs: Any) -> MagicMock:
        return MagicMock()

    def _filterable_dataframe(df: Any, *, key: str, **kwargs: Any) -> None:
        fake_st.tables[key] = df

    module.kpi_row = _kpi_row  # type: ignore[attr-defined]
    module.bar_chart = _bar_chart  # type: ignore[attr-defined]
    module.line_chart = _line_chart  # type: ignore[attr-defined]
    module.filterable_dataframe = _filterable_dataframe  # type: ignore[attr-defined]
    return module


def _run_page(*, multiselect_values: dict[str, list[Any]] | None = None) -> _FakeStreamlit:
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
    mock_sdk.subjects.list.return_value = [
        SimpleNamespace(subject_key="SUBJ-001", site_name="Site A", deleted=False),
        SimpleNamespace(subject_key="SUBJ-002", site_name="Site B", deleted=False),
    ]
    mock_sdk.forms.list.return_value = [
        SimpleNamespace(form_key="AE", form_name="Adverse Event"),
        SimpleNamespace(form_key="PD", form_name="Protocol Deviation"),
    ]
    mock_sdk.records.list.return_value = [
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
        def __init__(self) -> None:
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
            "imednet_workflows.extraction_engine",
            "imednet_workflows.query_management",
        )
    }
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_module
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
    return {entry["label"]: entry["value"] for entry in metrics}


def test_reporting_dashboard_renders_expected_kpis_and_site_aggregation() -> None:
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
