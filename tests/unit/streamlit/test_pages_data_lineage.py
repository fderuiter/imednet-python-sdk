"""Unit tests for the Data Lineage Explorer Streamlit page."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from imednet.models.reporting import AdverseEvent
from imednet.models.study_config import MappingRule, StudyConfiguration
from imednet_workflows.extraction_engine import ExtractionResult

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"
PAGE_PATH = PACKAGE_ROOT / "pages" / "data_lineage.py"
MODULE_NAME = "imednet_streamlit.pages.data_lineage"


class _FakeContextManager:
    """Test suite for  FakeContextManager."""

    def __enter__(self) -> _FakeContextManager:
        """Helper function to   enter  ."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Helper function to   exit  ."""
        pass

    # Make it usable as a column mock with common widget methods
    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        """Helper function to metric."""
        pass

    def button(self, label: str, **kwargs: Any) -> bool:
        """Helper function to button."""
        return False

    def text_input(self, label: str, **kwargs: Any) -> str:
        """Helper function to text input."""
        return str(kwargs.get("value", ""))

    def selectbox(self, label: str, options: list[Any], index: int = 0, **kwargs: Any) -> Any:
        """Helper function to selectbox."""
        return options[index]

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        """Helper function to dataframe."""
        pass


class _FakeStreamlit:
    """Test suite for  FakeStreamlit."""

    def __init__(self) -> None:
        """Initialize the test object."""
        self.session_state: dict[str, Any] = {"_imednet_connected": True}
        self.success_calls: list[str] = []
        self.warning_calls: list[str] = []
        self.info_calls: list[str] = []
        self.error_calls: list[str] = []
        self.button_presses: set[str] = set()
        self.metric_calls: list[dict[str, Any]] = []
        self.dataframe_calls: list[Any] = []
        self.json_calls: list[Any] = []
        self.text_input_values: dict[str, str] = {}

    def title(self, value: str) -> None:
        """Helper function to title."""
        pass

    def header(self, value: str) -> None:
        pass

    def subheader(self, value: str) -> None:
        """Helper function to subheader."""
        pass

    def markdown(self, value: str, **kwargs: Any) -> None:
        """Helper function to markdown."""
        pass

    def info(self, value: str) -> None:
        """Helper function to info."""
        self.info_calls.append(value)

    def success(self, value: str) -> None:
        """Helper function to success."""
        self.success_calls.append(value)

    def warning(self, value: str) -> None:
        """Helper function to warning."""
        self.warning_calls.append(value)

    def error(self, value: str) -> None:
        """Helper function to error."""
        self.error_calls.append(value)

    def divider(self) -> None:
        """Helper function to divider."""
        pass

    def json(self, value: Any) -> None:
        """Helper function to json."""
        self.json_calls.append(value)

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        """Helper function to dataframe."""
        self.dataframe_calls.append(df)

    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        """Helper function to metric."""
        self.metric_calls.append({"label": label, "value": value})

    def button(self, label: str, **kwargs: Any) -> bool:
        """Helper function to button."""
        key = str(kwargs.get("key") or label)
        if kwargs.get("disabled", False):
            return False
        return key in self.button_presses

    def columns(self, spec: Any) -> list[_FakeContextManager]:
        """Helper function to columns."""
        count = spec if isinstance(spec, int) else len(spec)
        cols = []
        for _ in range(count):
            col = _FakeContextManager()
            col.metric = self.metric  # type: ignore[attr-defined]
            col.button = self.button  # type: ignore[attr-defined]
            col.text_input = self.text_input  # type: ignore[attr-defined]
            col.selectbox = self.selectbox  # type: ignore[attr-defined]
            col.dataframe = self.dataframe  # type: ignore[attr-defined]
            cols.append(col)
        return cols

    def selectbox(self, label: str, options: list[Any], index: int = 0, **kwargs: Any) -> Any:
        """Helper function to selectbox."""
        return options[index]

    def text_input(self, label: str, **kwargs: Any) -> str:
        """Helper function to text input."""
        key = str(kwargs.get("key") or label)
        if key in self.text_input_values:
            return self.text_input_values[key]
        return str(kwargs.get("value", ""))

    def text_area(self, label: str, **kwargs: Any) -> str:
        """Helper function to text area."""
        return str(kwargs.get("value", ""))

    def expander(self, label: str, **kwargs: Any) -> _FakeContextManager:
        """Helper function to expander."""
        return _FakeContextManager()

    def caption(self, value: str) -> None:
        """Helper function to caption."""
        pass

    def progress(self, value: float) -> None:
        """Helper function to progress."""
        pass


def _make_fake_records() -> list[Any]:
    """Helper function to  make fake records."""
    return [
        SimpleNamespace(
            record_id=1,
            form_key="AE_FORM",
            subject_key="SUBJ-001",
            record_data={"ae_term": "headache", "aeSeverity": "MILD"},
        ),
        SimpleNamespace(
            record_id=2,
            form_key="AE_FORM",
            subject_key="SUBJ-002",
            record_data={"ae_term": "nausea", "aeSeverity": "MODERATE"},
        ),
    ]


def _make_extraction() -> ExtractionResult:
    """Helper function to  make extraction."""
    ae1 = AdverseEvent(
        subjectKey="SUBJ-001",
        aeTerm="headache",
        aeSeverity="MILD",
    )
    ae2 = AdverseEvent(
        subjectKey="SUBJ-002",
        aeTerm="nausea",
        aeSeverity="MODERATE",
    )
    return ExtractionResult(adverse_events=[ae1, ae2])


def _run_data_lineage(
    fake_st: _FakeStreamlit,
    *,
    study_key: str = "STUDY-01",
) -> None:
    """Helper function to  run data lineage."""
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "subheader",
        "header",
        "markdown",
        "info",
        "success",
        "warning",
        "error",
        "button",
        "columns",
        "selectbox",
        "text_input",
        "text_area",
        "divider",
        "json",
        "dataframe",
        "metric",
        "expander",
        "caption",
        "progress",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: MagicMock()  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: study_key  # type: ignore[attr-defined]

    # Fake CachedRecordsLoader
    fake_records = _make_fake_records()
    fake_extraction = _make_extraction()

    class _FakeLoader:
        """Test suite for  FakeLoader."""

        def __init__(self, sdk: object) -> None:
            """Initialize the test object."""
            pass

        def load_records(self, sk: str) -> list[Any]:
            """Helper function to load records."""
            return fake_records

    fake_workflows_module = ModuleType("imednet_workflows")
    fake_workflows_module.CachedRecordsLoader = _FakeLoader  # type: ignore[attr-defined]

    fake_engine_module = ModuleType("imednet_workflows.extraction_engine")
    fake_engine_module.ExtractionResult = ExtractionResult  # type: ignore[attr-defined]
    fake_engine_module.extract_canonical_records = (  # type: ignore[attr-defined]
        lambda records, config: fake_extraction
    )

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_workflows",
            "imednet_workflows.extraction_engine",
            MODULE_NAME,
        )
    }
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_workflows"] = fake_workflows_module
        sys.modules["imednet_workflows.extraction_engine"] = fake_engine_module
        module_spec = importlib.util.spec_from_file_location(MODULE_NAME, PAGE_PATH)
        assert module_spec is not None
        assert module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[MODULE_NAME] = module
        module_spec.loader.exec_module(module)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_data_lineage_not_connected() -> None:
    """Page shows info when user is not connected."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["_imednet_connected"] = False
    _run_data_lineage(fake_st)
    assert any("connect" in msg.lower() for msg in fake_st.info_calls)


def test_data_lineage_no_records_prompt() -> None:
    """Before loading records, user is prompted to click the load button."""
    fake_st = _FakeStreamlit()
    _run_data_lineage(fake_st)
    assert any("load" in msg.lower() or "click" in msg.lower() for msg in fake_st.info_calls)


def test_data_lineage_load_records() -> None:
    """After pressing load button, records are stored and metrics rendered."""
    fake_st = _FakeStreamlit()
    fake_st.button_presses = {"lineage_load_btn"}
    _run_data_lineage(fake_st)

    assert isinstance(fake_st.session_state.get("_lineage_records"), list)
    assert isinstance(fake_st.session_state.get("_lineage_extraction"), ExtractionResult)
    assert any("loaded" in msg.lower() for msg in fake_st.success_calls)


def test_data_lineage_metric_counts() -> None:
    """Metric tiles reflect correct counts from extraction."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["_lineage_extraction"] = _make_extraction()
    _run_data_lineage(fake_st)

    labels = [m["label"] for m in fake_st.metric_calls]
    assert any("Adverse" in label for label in labels)


def test_data_lineage_drill_into_ae() -> None:
    """Drilling into AE updates domain and shows record table."""
    fake_st = _FakeStreamlit()
    extraction = _make_extraction()
    fake_st.session_state["_lineage_extraction"] = extraction
    fake_st.button_presses = {"lineage_drill_AE"}
    _run_data_lineage(fake_st)

    assert fake_st.session_state.get("_lineage_domain") == "AE"


def test_data_lineage_lineage_trace_no_config() -> None:
    """Lineage trace renders without crashing when no config is set."""
    fake_st = _FakeStreamlit()
    extraction = _make_extraction()
    fake_st.session_state["_lineage_extraction"] = extraction
    fake_st.session_state["_lineage_domain"] = "AE"
    fake_st.session_state["_lineage_selected_idx"] = 0
    _run_data_lineage(fake_st)

    # At least one JSON pane should have been rendered (canonical model)
    assert fake_st.json_calls


def test_data_lineage_lineage_trace_with_config() -> None:
    """Lineage trace with a StudyConfiguration renders mapping rules."""
    fake_st = _FakeStreamlit()
    extraction = _make_extraction()
    records = _make_fake_records()
    config = StudyConfiguration(
        studyKey="STUDY-01",
        mappings=[
            MappingRule(
                domain="AE",
                targetField="aeTerm",
                sourceFormKey="AE_FORM",
                sourceVariableName="ae_term",
            )
        ],
    )
    fake_st.session_state["_lineage_extraction"] = extraction
    fake_st.session_state["_lineage_records"] = records
    fake_st.session_state["_lineage_config"] = config
    fake_st.session_state["_lineage_domain"] = "AE"
    fake_st.session_state["_lineage_selected_idx"] = 0
    _run_data_lineage(fake_st)

    # Should render canonical model as JSON
    assert fake_st.json_calls


def test_data_lineage_no_records_in_domain() -> None:
    """Info message is shown when the selected domain has no records."""
    fake_st = _FakeStreamlit()
    empty_extraction = ExtractionResult()  # no records
    fake_st.session_state["_lineage_extraction"] = empty_extraction
    fake_st.session_state["_lineage_domain"] = "PD"
    _run_data_lineage(fake_st)

    assert any(
        "no pd records" in msg.lower() or "no protocol" in msg.lower() for msg in fake_st.info_calls
    )


def test_data_lineage_redact_sensitive_keys() -> None:
    """Raw record display must never expose sensitive fields in plaintext."""
    from imednet_streamlit.pages.data_lineage import _redact_sensitive

    data = {
        "ae_term": "headache",
        "patient_name": "John Doe",
        "ssn": "000-00-0000",
        "dob": "1990-01-01",
        "subject_key": "SUBJ-001",
        "api_key": "secret_api",
        "token": "secret_token",
        "nested": {
            "password": "secret_password",
            "details": [
                {"security_key": "secret_key"},
                {"phone": "555-1234"},
                {"label": "ok"}
            ],
        },
        "severity": "MILD",
    }
    redacted = _redact_sensitive(data)
    assert redacted["ae_term"] == "headache"
    assert redacted["severity"] == "MILD"
    assert redacted["subject_key"] == "SUBJ-001"
    assert redacted["api_key"] == "***"
    assert redacted["token"] == "***"
    assert redacted["nested"]["password"] == "***"
    assert redacted["nested"]["details"][0]["security_key"] == "***"
    assert redacted["patient_name"] == "***MASKED***"
    assert redacted["ssn"] == "***MASKED***"
    assert redacted["dob"] == "***MASKED***"
    assert redacted["nested"]["details"][1]["phone"] == "***MASKED***"
    assert redacted["nested"]["details"][2]["label"] == "ok"
