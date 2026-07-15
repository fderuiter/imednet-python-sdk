"""Unit tests for pages setup wizard."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

from imednet.models.study_config import StudyConfiguration

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


class _FakeColumn:
    """Test suite for  FakeColumn."""

    def __init__(self, parent: "_FakeStreamlit") -> None:
        """Initialize the test object."""
        self._parent = parent

    def button(self, label: str, **kwargs: Any) -> bool:
        """Helper function to button."""
        return self._parent.button(label, **kwargs)

    def selectbox(self, label: str, options: list[str], **kwargs: Any) -> str:
        """Helper function to selectbox."""
        return self._parent.selectbox(label, options, **kwargs)

    def text_input(self, label: str, **kwargs: Any) -> str:
        """Helper function to text input."""
        return self._parent.text_input(label, **kwargs)

    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        """Helper function to metric."""
        self._parent.metric(label, value, **kwargs)


class _FakeContextManager:
    """Test suite for  FakeContextManager."""

    def __enter__(self) -> "_FakeContextManager":
        """Helper function to   enter  ."""
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Helper function to   exit  ."""
        return None


class _FakeStreamlit:
    """Test suite for  FakeStreamlit."""

    def __init__(self) -> None:
        """Initialize the test object."""
        self.session_state: dict[str, Any] = {
            "_imednet_connected": True,
            "_imednet_study_key": "STUDY",
        }
        self.button_presses: set[str] = set()
        self.selectbox_values: dict[str, str] = {}
        self.text_input_values: dict[str, str] = {}
        self.multiselect_values: dict[str, list[str]] = {}
        self.slider_value: int | None = None
        self.download_calls: list[dict[str, Any]] = []
        self.metric_calls: list[dict[str, Any]] = []
        self.success_calls: list[str] = []
        self.warning_calls: list[str] = []
        self.info_calls: list[str] = []
        self.error_calls: list[str] = []
        self.titles: list[str] = []
        self.markdown_calls: list[str] = []
        self.subheader_calls: list[str] = []
        self.code_calls: list[str] = []
        self.expander_calls: list[tuple[str, bool]] = []

    def title(self, value: str) -> None:
        """Helper function to title."""
        self.titles.append(value)

    def header(self, value: str) -> None:
        pass

    def subheader(self, value: str) -> None:
        """Helper function to subheader."""
        self.subheader_calls.append(value)

    def markdown(self, value: str) -> None:
        """Helper function to markdown."""
        self.markdown_calls.append(value)

    def caption(self, value: str) -> None:
        """Helper function to caption."""
        return None

    def expander(self, label: str, *, expanded: bool = False) -> _FakeContextManager:
        """Helper function to expander."""
        self.expander_calls.append((label, expanded))
        return _FakeContextManager()

    def code(self, body: str, *, language: str = "") -> None:
        """Helper function to code."""
        self.code_calls.append(body)

    def progress(self, value: float) -> None:
        """Helper function to progress."""
        return None

    def success(self, value: str) -> None:
        """Helper function to success."""
        self.success_calls.append(value)

    def warning(self, value: str) -> None:
        """Helper function to warning."""
        self.warning_calls.append(value)

    def info(self, value: str) -> None:
        """Helper function to info."""
        self.info_calls.append(value)

    def error(self, value: str) -> None:
        """Helper function to error."""
        self.error_calls.append(value)

    def button(self, label: str, **kwargs: Any) -> bool:
        """Helper function to button."""
        key = str(kwargs.get("key") or label)
        if kwargs.get("disabled", False):
            return False
        return key in self.button_presses

    def columns(self, spec: int | list[Any]) -> list[_FakeColumn]:
        """Helper function to columns."""
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeColumn(self) for _ in range(count)]

    def selectbox(self, label: str, options: list[str], **kwargs: Any) -> str:
        """Helper function to selectbox."""
        key = str(kwargs.get("key") or label)
        if key in self.selectbox_values and self.selectbox_values[key] in options:
            return self.selectbox_values[key]
        return str(options[0]) if options else ""

    def text_input(self, label: str, **kwargs: Any) -> str:
        """Helper function to text input."""
        key = str(kwargs.get("key") or label)
        if key in self.text_input_values:
            return self.text_input_values[key]
        value = kwargs.get("value", "")
        return str(value) if value is not None else ""

    def multiselect(self, label: str, options: list[str], **kwargs: Any) -> list[str]:
        """Helper function to multiselect."""
        key = str(kwargs.get("key") or label)
        if key in self.multiselect_values:
            return self.multiselect_values[key]
        default = kwargs.get("default", [])
        invalid_defaults = [str(value) for value in default if str(value) not in options]
        if invalid_defaults:
            raise ValueError(f"Invalid default values: {invalid_defaults}")
        return [str(value) for value in default]

    def slider(self, label: str, **kwargs: Any) -> int:
        """Helper function to slider."""
        if self.slider_value is not None:
            return self.slider_value
        return int(kwargs.get("value", kwargs.get("min_value", 0)))

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        """Helper function to dataframe."""
        return None

    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        """Helper function to metric."""
        self.metric_calls.append({"label": label, "value": value})

    def json(self, value: Any) -> None:
        """Helper function to json."""
        return None

    def download_button(self, **kwargs: Any) -> None:
        """Helper function to download button."""
        self.download_calls.append(kwargs)


class _WidgetOwnedSessionState(dict[str, Any]):
    """Test suite for  WidgetOwnedSessionState."""

    def __init__(self, initial_state: dict[str, Any]) -> None:
        """Initialize the test object."""
        super().__init__(initial_state)
        self._widget_owned_keys: set[str] = set()

    def lock_widget_key(self, key: str) -> None:
        """Helper function to lock widget key."""
        self._widget_owned_keys.add(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Helper function to   setitem  ."""
        if key in self._widget_owned_keys:
            raise RuntimeError(f"session_state key '{key}' is widget-owned")
        super().__setitem__(key, value)


class _StrictWidgetStateFakeStreamlit(_FakeStreamlit):
    """Test suite for  StrictWidgetStateFakeStreamlit."""

    def __init__(self) -> None:
        """Initialize the test object."""
        super().__init__()
        self.session_state = _WidgetOwnedSessionState(dict(self.session_state))

    def selectbox(self, label: str, options: list[str], **kwargs: Any) -> str:
        """Helper function to selectbox."""
        value = super().selectbox(label, options, **kwargs)
        key = str(kwargs.get("key") or label)
        dict.__setitem__(self.session_state, key, value)
        self.session_state.lock_widget_key(key)
        return value


def _run_setup_wizard(
    fake_st: _FakeStreamlit,
    *,
    get_sdk: Any | None = None,
    get_study_key: Any | None = None,
) -> None:
    """Helper function to  run setup wizard."""
    page_path = PACKAGE_ROOT / "pages" / "setup_wizard.py"
    module_name = "imednet_streamlit.pages.setup_wizard"

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "subheader",
        "header",
        "markdown",
        "caption",
        "expander",
        "code",
        "progress",
        "success",
        "warning",
        "info",
        "error",
        "button",
        "columns",
        "selectbox",
        "text_input",
        "multiselect",
        "slider",
        "dataframe",
        "metric",
        "json",
        "download_button",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))

    records = [
        SimpleNamespace(
            record_id=1,
            form_key="AE_FORM",
            subject_key="SUBJ-001",
            record_data={"AE_TERM": "y"},
        ),
        SimpleNamespace(
            record_id=2,
            form_key="AE_FORM",
            subject_key="SUBJ-002",
            record_data={"AE_TERM": "n"},
        ),
    ]

    fields = {
        "AE_TERM": SimpleNamespace(
            variable_name="AE_TERM",
            label="Adverse Event",
            population_rate=100.0,
            inferred_type="string",
            unique_count=2,
            unique_values=["y", "n"],
        )
    }
    profiles = {
        "AE_FORM": SimpleNamespace(
            form_key="AE_FORM",
            form_name="Adverse Events",
            record_count=2,
            fields=fields,
        )
    }

    class _FakeLoader:
        """Test suite for  FakeLoader."""

        def __init__(self, sdk: object) -> None:
            """Initialize the test object."""
            self.sdk = sdk

        def load_records(self, study_key: str) -> list[Any]:
            """Helper function to load records."""
            return records

    class _FakeProfiler:
        """Test suite for  FakeProfiler."""

        def __init__(self, sdk: object, loader: object) -> None:
            """Initialize the test object."""
            self.sdk = sdk
            self.loader = loader

        def profile_records(
            self, study_key: str, *, records: list[Any] | None = None
        ) -> dict[str, Any]:
            """Helper function to profile records."""
            return profiles

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = get_sdk or (lambda: object())  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = get_study_key or (  # type: ignore[attr-defined]
        lambda: str(fake_st.session_state.get("_imednet_study_key", "STUDY"))
    )

    fake_workflows_module = ModuleType("imednet_workflows")
    fake_workflows_module.CachedRecordsLoader = _FakeLoader  # type: ignore[attr-defined]
    fake_workflows_module.SchemaProfiler = _FakeProfiler  # type: ignore[attr-defined]

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_workflows",
            module_name,
        )
    }
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_workflows"] = fake_workflows_module
        module_spec = importlib.util.spec_from_file_location(module_name, page_path)
        assert module_spec is not None and module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original


def test_setup_wizard_scan_and_next_step() -> None:
    """Test that setup wizard scan and next step."""
    fake_st = _FakeStreamlit()
    fake_st.button_presses = {"wizard_scan"}
    _run_setup_wizard(fake_st)

    assert fake_st.session_state["wizard_step"] == 1
    assert fake_st.session_state["discovered_schema"] is not None
    assert isinstance(fake_st.session_state["mapping_config"], StudyConfiguration)

    fake_st.button_presses = {"wizard_next"}
    _run_setup_wizard(fake_st)
    assert fake_st.session_state["wizard_step"] == 2


def test_setup_wizard_scan_post_scan_rerender_respects_widget_owned_state() -> None:
    """Test that setup wizard scan post scan rerender respects widget owned state."""
    fake_st = _StrictWidgetStateFakeStreamlit()
    fake_st.button_presses = {"wizard_scan"}

    _run_setup_wizard(fake_st)

    assert fake_st.session_state["wizard_target_form_ae"] == "AE_FORM"
    assert fake_st.session_state["wizard_target_form_pd"] == "AE_FORM"
    assert fake_st.session_state["wizard_target_form_dd"] == "AE_FORM"


def test_setup_wizard_renders_design_specification_sections() -> None:
    """Test that setup wizard renders design specification sections."""
    fake_st = _FakeStreamlit()
    _run_setup_wizard(fake_st)

    joined_markdown = "\n".join(fake_st.markdown_calls)
    joined_subheaders = "\n".join(fake_st.subheader_calls)
    assert ("UX Design Specification", False) in fake_st.expander_calls
    assert any("Step 1: Scan & Profile" in body for body in fake_st.code_calls)
    assert "Flowchart / state transitions" in joined_subheaders
    assert "Wireframe mapped to session state" in joined_subheaders
    assert "UX review: Streamlit multi-page alignment" in joined_subheaders


def test_setup_wizard_mapping_normalization_preview_and_export() -> None:
    """Test that setup wizard mapping normalization preview and export."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 2
    fake_st.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY")
    fake_st.session_state["discovered_schema"] = {
        "forms": [
            {
                "form_key": "AE_FORM",
                "form_name": "Adverse Events",
                "record_count": 2,
                "fields": [
                    {
                        "variable_name": "AE_TERM",
                        "label": "Adverse Event",
                        "population_rate": 100.0,
                        "inferred_type": "string",
                        "unique_count": 2,
                        "unique_values": ["y", "n"],
                    }
                ],
            }
        ],
        "sample_records": [
            {
                "record_id": 1,
                "form_key": "AE_FORM",
                "subject_key": "SUBJ-001",
                "record_data": {"AE_TERM": "y"},
            }
        ],
    }
    fake_st.session_state["wizard_target_form_ae"] = "AE_FORM"
    fake_st.session_state["wizard_target_form_pd"] = "AE_FORM"
    fake_st.session_state["wizard_target_form_dd"] = "AE_FORM"
    fake_st.selectbox_values = {
        "wizard_map_form_AE.ae_term": "AE_FORM",
        "wizard_map_field_AE.ae_term": "AE_TERM",
    }
    _run_setup_wizard(fake_st)

    config = fake_st.session_state["mapping_config"]
    assert len(config.mappings) == 1
    assert config.mappings[0].target_field == "ae_term"

    fake_st.session_state["wizard_step"] = 3
    fake_st.selectbox_values["wizard_terminology_mapping"] = "AE.ae_term"
    fake_st.text_input_values = {
        "wizard_norm_AE.ae_term_y": "true",
        "wizard_norm_AE.ae_term_n": "false",
    }
    _run_setup_wizard(fake_st)
    assert config.terminology_lookups["AE.ae_term"] == {"y": "true", "n": "false"}

    fake_st.session_state["wizard_step"] = 4
    _run_setup_wizard(fake_st)
    assert fake_st.session_state["validation_report"]["preview_rows"] == 1

    fake_st.session_state["wizard_step"] = 5
    _run_setup_wizard(fake_st)
    assert fake_st.download_calls
    assert fake_st.download_calls[-1]["file_name"] == "study_study_configuration.json"


def test_setup_wizard_mapping_falls_back_when_saved_form_is_missing() -> None:
    """Test that setup wizard mapping falls back when saved form is missing."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 2
    fake_st.session_state["mapping_config"] = StudyConfiguration.from_json(
        {
            "studyKey": "STUDY",
            "mappings": [
                {
                    "domain": "AE",
                    "targetField": "ae_term",
                    "sourceFormKey": "MISSING_FORM",
                    "sourceVariableName": "AE_TERM",
                }
            ],
        }
    )
    fake_st.session_state["discovered_schema"] = {
        "forms": [
            {
                "form_key": "AE_FORM",
                "form_name": "Adverse Events",
                "record_count": 1,
                "fields": [{"variable_name": "AE_TERM"}],
            }
        ],
        "sample_records": [],
    }
    fake_st.session_state["wizard_target_form_ae"] = "AE_FORM"
    fake_st.session_state["wizard_target_form_pd"] = "AE_FORM"
    fake_st.session_state["wizard_target_form_dd"] = "AE_FORM"

    _run_setup_wizard(fake_st)

    assert fake_st.session_state["mapping_config"].mappings == []


def test_setup_wizard_preview_filters_invalid_saved_widget_types() -> None:
    """Test that setup wizard preview filters invalid saved widget types."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 4
    fake_st.session_state["mapping_config"] = StudyConfiguration.from_json(
        {
            "studyKey": "STUDY",
            "mappings": [
                {
                    "domain": "AE",
                    "targetField": "ae_term",
                    "sourceFormKey": "AE_FORM",
                    "sourceVariableName": "AE_TERM",
                }
            ],
            "widgets": [
                {"widgetId": "widget-1", "type": "pie_chart", "title": "Pie", "domain": "AE"}
            ],
        }
    )
    fake_st.session_state["discovered_schema"] = {
        "forms": [],
        "sample_records": [
            {
                "record_id": 1,
                "form_key": "AE_FORM",
                "subject_key": "SUBJ-001",
                "record_data": {"AE_TERM": "y"},
            }
        ],
    }

    _run_setup_wizard(fake_st)

    assert fake_st.session_state["validation_report"]["preview_rows"] == 1
    assert [widget.type for widget in fake_st.session_state["mapping_config"].widgets] == [
        "kpi_card",
        "bar_chart",
    ]


def test_setup_wizard_save_managed_database(monkeypatch: Any) -> None:
    """Test that setup wizard save managed database."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 5
    fake_st.session_state["_imednet_study_key"] = "STUDY-123"
    fake_st.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY-123")
    fake_st.button_presses = {"wizard_save_managed"}

    class MockStore:
        """Test suite for MockStore."""

        def commit_config(self, study_key, config, user, desc):
            """Helper function to commit config."""
            self.study_key = study_key
            self.user = user

    mock_store = MockStore()
    monkeypatch.setattr(
        "imednet_workflows.config_version_control.ConfigVersionStore", lambda: mock_store
    )

    _run_setup_wizard(fake_st)

    assert mock_store.study_key == "STUDY-123"
    assert "Successfully saved" in fake_st.success_calls[-1]


def test_setup_wizard_save_managed_reports_error(monkeypatch: Any) -> None:
    """Test that setup wizard save managed reports error."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 5
    fake_st.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY")
    fake_st.button_presses = {"wizard_save_managed"}

    class MockStore:
        """Test suite for MockStore."""

        def commit_config(self, study_key, config, user, desc):
            """Helper function to commit config."""
            raise OSError("boom")

    monkeypatch.setattr(
        "imednet_workflows.config_version_control.ConfigVersionStore", lambda: MockStore()
    )

    _run_setup_wizard(fake_st)

    assert "Unable to save configuration:" in fake_st.error_calls[-1]


def test_setup_wizard_shows_prerequisite_info_messages() -> None:
    """Test that setup wizard shows prerequisite info messages."""
    step_one = _FakeStreamlit()
    _run_setup_wizard(step_one)
    assert step_one.info_calls[-1] == "Run scan to discover forms and field candidates."

    step_two = _FakeStreamlit()
    step_two.session_state["wizard_step"] = 2
    step_two.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY")
    _run_setup_wizard(step_two)
    assert step_two.info_calls[-1] == "No profiled forms available yet. Complete Step 1 first."

    step_three = _FakeStreamlit()
    step_three.session_state["wizard_step"] = 3
    step_three.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY")
    _run_setup_wizard(step_three)
    assert step_three.info_calls[-1] == "Add field mappings first in Step 2."

    step_four = _FakeStreamlit()
    step_four.session_state["wizard_step"] = 4
    step_four.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY")
    _run_setup_wizard(step_four)
    assert step_four.info_calls[-1] == "Create mappings in Step 2 before previewing."


def test_setup_wizard_handles_connection_and_auth_failures() -> None:
    """Test that setup wizard handles connection and auth failures."""
    disconnected = _FakeStreamlit()
    disconnected.session_state["_imednet_connected"] = False
    _run_setup_wizard(disconnected)
    assert disconnected.info_calls[-1] == (
        "Please connect from the sidebar to configure and publish a study mapping."
    )

    auth_failure = _FakeStreamlit()

    def _raise_runtime_error() -> object:
        """Helper function to  raise runtime error."""
        raise RuntimeError("missing credentials")

    _run_setup_wizard(auth_failure, get_sdk=_raise_runtime_error)
    assert auth_failure.error_calls[-1] == "missing credentials"


def test_setup_wizard_snapshot_controls_and_navigation_work() -> None:
    """Test that setup wizard snapshot controls and navigation work."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 3
    fake_st.session_state["mapping_config"] = StudyConfiguration.from_json(
        {
            "studyKey": "STUDY",
            "mappings": [
                {
                    "domain": "AE",
                    "targetField": "ae_term",
                    "sourceFormKey": "AE_FORM",
                    "sourceVariableName": "AE_TERM",
                }
            ],
            "terminologyLookups": {"AE.ae_term": {"y": "yes"}},
        }
    )
    fake_st.session_state["discovered_schema"] = {
        "forms": [
            {
                "form_key": "AE_FORM",
                "form_name": "Adverse Events",
                "record_count": 1,
                "fields": [
                    {
                        "variable_name": "AE_TERM",
                        "label": "Adverse Event",
                        "population_rate": 100.0,
                        "inferred_type": "string",
                        "unique_count": 1,
                        "unique_values": ["y"],
                    }
                ],
            }
        ],
        "sample_records": [],
    }
    fake_st.selectbox_values["wizard_terminology_mapping"] = "AE.ae_term"

    fake_st.button_presses = {"wizard_clone_snapshot"}
    _run_setup_wizard(fake_st)
    assert fake_st.success_calls[-1] == "Configuration snapshot saved."

    fake_st.button_presses = {"wizard_undo_snapshot"}
    _run_setup_wizard(fake_st)
    assert fake_st.success_calls[-1] == "Reverted to previous configuration snapshot."

    fake_st.button_presses = {"wizard_reset_normalizations"}
    _run_setup_wizard(fake_st)
    assert fake_st.success_calls[-1] == "Terminology normalizations reset."
    assert fake_st.session_state["mapping_config"].terminology_lookups == {}

    fake_st.button_presses = {"wizard_prev"}
    _run_setup_wizard(fake_st)
    assert fake_st.session_state["wizard_step"] == 2


def test_setup_wizard_undo_without_snapshot_and_nav_button_paths() -> None:
    """Test that setup wizard undo without snapshot and nav button paths."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 3
    fake_st.session_state["mapping_config"] = StudyConfiguration.from_json(
        {
            "studyKey": "STUDY",
            "mappings": [
                {
                    "domain": "AE",
                    "targetField": "ae_term",
                    "sourceFormKey": "AE_FORM",
                    "sourceVariableName": "AE_TERM",
                }
            ],
        }
    )
    fake_st.session_state["discovered_schema"] = {
        "forms": [
            {
                "form_key": "AE_FORM",
                "form_name": "Adverse Events",
                "record_count": 1,
                "fields": [
                    {
                        "variable_name": "AE_TERM",
                        "label": "Adverse Event",
                        "population_rate": 100.0,
                        "inferred_type": "string",
                        "unique_count": 1,
                        "unique_values": ["y"],
                    }
                ],
            }
        ],
        "sample_records": [],
    }
    fake_st.selectbox_values["wizard_terminology_mapping"] = "AE.ae_term"

    fake_st.button_presses = {"wizard_undo_snapshot"}
    _run_setup_wizard(fake_st)
    assert fake_st.warning_calls[-1] == "No snapshots available to undo."

    fake_st.button_presses = {"wizard_nav_2"}
    _run_setup_wizard(fake_st)
    assert fake_st.session_state["wizard_step"] == 2


def test_setup_wizard_preview_handles_empty_records() -> None:
    """Test that setup wizard preview handles empty records."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 4
    fake_st.session_state["mapping_config"] = StudyConfiguration.from_json(
        {
            "studyKey": "STUDY",
            "mappings": [
                {
                    "domain": "AE",
                    "targetField": "ae_term",
                    "sourceFormKey": "AE_FORM",
                    "sourceVariableName": "AE_TERM",
                }
            ],
        }
    )
    fake_st.session_state["discovered_schema"] = {
        "forms": [
            {
                "form_key": "AE_FORM",
                "form_name": "Adverse Events",
                "record_count": 0,
                "fields": [],
            }
        ],
        "sample_records": [],
    }

    _run_setup_wizard(fake_st)

    assert fake_st.info_calls[-1] == "No sample records available to preview."
