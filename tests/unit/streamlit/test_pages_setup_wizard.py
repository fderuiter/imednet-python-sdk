from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

from imednet.models.study_config import StudyConfiguration

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


class _FakeColumn:
    def __init__(self, parent: "_FakeStreamlit") -> None:
        self._parent = parent

    def button(self, label: str, **kwargs: Any) -> bool:
        return self._parent.button(label, **kwargs)

    def selectbox(self, label: str, options: list[str], **kwargs: Any) -> str:
        return self._parent.selectbox(label, options, **kwargs)

    def text_input(self, label: str, **kwargs: Any) -> str:
        return self._parent.text_input(label, **kwargs)

    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        self._parent.metric(label, value, **kwargs)


class _FakeStreamlit:
    def __init__(self) -> None:
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
        self.error_calls: list[str] = []
        self.titles: list[str] = []

    def title(self, value: str) -> None:
        self.titles.append(value)

    def subheader(self, value: str) -> None:
        return None

    def markdown(self, value: str) -> None:
        return None

    def caption(self, value: str) -> None:
        return None

    def progress(self, value: float) -> None:
        return None

    def success(self, value: str) -> None:
        self.success_calls.append(value)

    def warning(self, value: str) -> None:
        return None

    def info(self, value: str) -> None:
        return None

    def error(self, value: str) -> None:
        self.error_calls.append(value)

    def button(self, label: str, **kwargs: Any) -> bool:
        key = str(kwargs.get("key") or label)
        if kwargs.get("disabled", False):
            return False
        return key in self.button_presses

    def columns(self, spec: int | list[Any]) -> list[_FakeColumn]:
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeColumn(self) for _ in range(count)]

    def selectbox(self, label: str, options: list[str], **kwargs: Any) -> str:
        key = str(kwargs.get("key") or label)
        if key in self.selectbox_values and self.selectbox_values[key] in options:
            return self.selectbox_values[key]
        return str(options[0]) if options else ""

    def text_input(self, label: str, **kwargs: Any) -> str:
        key = str(kwargs.get("key") or label)
        if key in self.text_input_values:
            return self.text_input_values[key]
        value = kwargs.get("value", "")
        return str(value) if value is not None else ""

    def multiselect(self, label: str, options: list[str], **kwargs: Any) -> list[str]:
        key = str(kwargs.get("key") or label)
        if key in self.multiselect_values:
            return self.multiselect_values[key]
        default = kwargs.get("default", [])
        invalid_defaults = [str(value) for value in default if str(value) not in options]
        if invalid_defaults:
            raise ValueError(f"Invalid default values: {invalid_defaults}")
        return [str(value) for value in default]

    def slider(self, label: str, **kwargs: Any) -> int:
        if self.slider_value is not None:
            return self.slider_value
        return int(kwargs.get("value", kwargs.get("min_value", 0)))

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        return None

    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        self.metric_calls.append({"label": label, "value": value})

    def json(self, value: Any) -> None:
        return None

    def download_button(self, **kwargs: Any) -> None:
        self.download_calls.append(kwargs)


def _run_setup_wizard(fake_st: _FakeStreamlit) -> None:
    page_path = PACKAGE_ROOT / "pages" / "setup_wizard.py"

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "subheader",
        "markdown",
        "caption",
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
        def __init__(self, sdk: object) -> None:
            self.sdk = sdk

        def load_records(self, study_key: str) -> list[Any]:
            return records

    class _FakeProfiler:
        def __init__(self, sdk: object, loader: object) -> None:
            self.sdk = sdk
            self.loader = loader

        def profile_records(
            self, study_key: str, *, records: list[Any] | None = None
        ) -> dict[str, Any]:
            return profiles

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_sdk = lambda: object()  # type: ignore[attr-defined]
    fake_auth_module.get_study_key = lambda: str(  # type: ignore[attr-defined]
        fake_st.session_state.get("_imednet_study_key", "STUDY")
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
        )
    }
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_workflows"] = fake_workflows_module
        runpy.run_path(str(page_path), run_name="__main__")
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original


def test_setup_wizard_scan_and_next_step() -> None:
    fake_st = _FakeStreamlit()
    fake_st.button_presses = {"wizard_scan"}
    _run_setup_wizard(fake_st)

    assert fake_st.session_state["wizard_step"] == 1
    assert fake_st.session_state["discovered_schema"] is not None
    assert isinstance(fake_st.session_state["mapping_config"], StudyConfiguration)

    fake_st.button_presses = {"wizard_next"}
    _run_setup_wizard(fake_st)
    assert fake_st.session_state["wizard_step"] == 2


def test_setup_wizard_mapping_normalization_preview_and_export() -> None:
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
        "wizard_map_form_AE.event_term": "AE_FORM",
        "wizard_map_field_AE.event_term": "AE_TERM",
    }
    _run_setup_wizard(fake_st)

    config = fake_st.session_state["mapping_config"]
    assert len(config.mappings) == 1
    assert config.mappings[0].target_field == "event_term"

    fake_st.session_state["wizard_step"] = 3
    fake_st.selectbox_values["wizard_terminology_mapping"] = "AE.event_term"
    fake_st.text_input_values = {
        "wizard_norm_AE.event_term_y": "true",
        "wizard_norm_AE.event_term_n": "false",
    }
    _run_setup_wizard(fake_st)
    assert config.terminology_lookups["AE.event_term"] == {"y": "true", "n": "false"}

    fake_st.session_state["wizard_step"] = 4
    _run_setup_wizard(fake_st)
    assert fake_st.session_state["validation_report"]["preview_rows"] == 1

    fake_st.session_state["wizard_step"] = 5
    _run_setup_wizard(fake_st)
    assert fake_st.download_calls
    assert fake_st.download_calls[-1]["file_name"] == "study_study_configuration.json"


def test_setup_wizard_mapping_falls_back_when_saved_form_is_missing() -> None:
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 2
    fake_st.session_state["mapping_config"] = StudyConfiguration.from_json(
        {
            "studyKey": "STUDY",
            "mappings": [
                {
                    "domain": "AE",
                    "targetField": "event_term",
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
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 4
    fake_st.session_state["mapping_config"] = StudyConfiguration.from_json(
        {
            "studyKey": "STUDY",
            "mappings": [
                {
                    "domain": "AE",
                    "targetField": "event_term",
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


def test_setup_wizard_save_local_sanitises_filename(tmp_path: Path, monkeypatch: Any) -> None:
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 5
    fake_st.session_state["_imednet_study_key"] = "../Bad/Name"
    fake_st.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY")
    fake_st.button_presses = {"wizard_save_local"}

    monkeypatch.setattr(Path, "cwd", classmethod(lambda cls: tmp_path))

    _run_setup_wizard(fake_st)

    output_file = tmp_path / ".imednet" / "configs" / "bad_name_study_configuration.json"
    assert output_file.is_file()
    assert fake_st.success_calls[-1] == f"Saved to {output_file}"


def test_setup_wizard_save_local_reports_oserror(monkeypatch: Any, tmp_path: Path) -> None:
    fake_st = _FakeStreamlit()
    fake_st.session_state["wizard_step"] = 5
    fake_st.session_state["mapping_config"] = StudyConfiguration(study_key="STUDY")
    fake_st.button_presses = {"wizard_save_local"}

    monkeypatch.setattr(Path, "cwd", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(
        Path,
        "write_text",
        lambda self, data, encoding=None: (_ for _ in ()).throw(OSError("boom")),
    )

    _run_setup_wizard(fake_st)

    assert fake_st.error_calls[-1] == "Unable to save configuration locally."
