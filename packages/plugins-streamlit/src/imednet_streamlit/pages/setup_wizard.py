from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

import pandas as pd
import streamlit as st

from imednet import ImednetSDK
from imednet.models.study_config import MappingRule, StudyConfiguration, WidgetConfig
from imednet_streamlit.auth import get_sdk, get_study_key
from imednet_workflows import CachedRecordsLoader, SchemaProfiler

_KEY_WIZARD_STEP = "wizard_step"
_KEY_DISCOVERED_SCHEMA = "discovered_schema"
_KEY_MAPPING_CONFIG = "mapping_config"
_KEY_VALIDATION_REPORT = "validation_report"
_KEY_HISTORY = "_wizard_snapshots"

_WIZARD_STEPS = (
    "Scan & Profile Study Structure",
    "Field Mapping",
    "Categorical Terminology Normalization",
    "Layout & Visual Configuration",
    "Export / Save",
)

_STATE_TRANSITION_DIAGRAM = """[Step 1: Scan & Profile]
  ├─ Scan button → discovered_schema, validation_report=None
  └─ Next (enabled when forms discovered) → Step 2

[Step 2: Field Mapping]
  ├─ Mapping selectors → mapping_config.mappings
  ├─ Previous → Step 1
  └─ Next → Step 3

[Step 3: Terminology Normalization]
  ├─ Normalization inputs → mapping_config.terminology_lookups
  ├─ Snapshot controls → _wizard_snapshots / mapping_config restore
  ├─ Previous → Step 2
  └─ Next → Step 4

[Step 4: Layout & Visual Configuration]
  ├─ Widget and layout controls → mapping_config.widgets
  ├─ Preview metrics → validation_report
  ├─ Previous → Step 3
  └─ Next → Step 5

[Step 5: Export / Save]
  ├─ Download JSON payload
  ├─ Save locally (.imednet/configs)
  └─ Previous → Step 4

Global transitions:
- Numbered nav buttons jump to any step (1..5)
- wizard_step is clamped to range 1..5 on every transition
"""

_SESSION_STATE_WIREFRAME = "\n".join(
    [
        "| Wizard step | Primary UI frame | Session state mutations |",
        "| --- | --- | --- |",
        (
            "| 1 | Scan action + AE/PD/DD form selectors | `discovered_schema`, "
            "`wizard_target_form_*`,<br>`validation_report` reset |"
        ),
        (
            "| 2 | Canonical target cards with source form/field/fallback controls | "
            "`mapping_config.mappings` |"
        ),
        (
            "| 3 | Mapping selector + raw→normalized value inputs + snapshot controls | "
            "`mapping_config.terminology_lookups`, `_wizard_snapshots`,"
            "<br>`mapping_config` restore/reset |"
        ),
        (
            "| 4 | Widget type multiselect + layout slider + preview metrics grid | "
            "`mapping_config.widgets`, `validation_report` |"
        ),
        (
            "| 5 | JSON preview + download + local save action | writes config file "
            "locally; no additional session mutation required |"
        ),
    ]
)

_UX_REVIEW_NOTES = "\n".join(
    [
        (
            "- The setup wizard remains a dedicated page in Streamlit multi-page "
            'navigation (`st.Page(..., title="Setup Wizard")`) and does not fork '
            "to separate app routes."
        ),
        (
            "- In-page progression is controlled by `wizard_step` so reruns preserve "
            "context while users move through numbered tabs and Previous/Next controls."
        ),
        (
            "- Guardrails are presented inline (`st.info`) when prerequisites are "
            "missing, which aligns with Streamlit's rerun-first interaction pattern."
        ),
    ]
)

_CANONICAL_FIELDS = (
    ("AE", "event_term", "Adverse Event Term"),
    ("AE", "severity", "Severity"),
    ("PD", "visit_date", "Visit Date"),
    ("PD", "status", "Progression Status"),
    ("DD", "disposition", "Disposition"),
)

_WIDGET_TYPES = ("kpi_card", "bar_chart", "line_chart", "data_table")


def _render_design_specification() -> None:
    st.markdown("### Wizard UX design specification")
    st.markdown("#### Flowchart / state transitions")
    st.code(_STATE_TRANSITION_DIAGRAM, language="text")
    st.markdown("#### Wireframe mapped to session state")
    st.markdown(_SESSION_STATE_WIREFRAME)
    st.markdown("#### UX review: Streamlit multi-page alignment")
    st.markdown(_UX_REVIEW_NOTES)


def _initialise_state(study_key: str) -> None:
    st.session_state.setdefault(_KEY_WIZARD_STEP, 1)
    st.session_state.setdefault(_KEY_DISCOVERED_SCHEMA, None)
    st.session_state.setdefault(_KEY_VALIDATION_REPORT, None)
    st.session_state.setdefault(_KEY_HISTORY, [])

    config = st.session_state.get(_KEY_MAPPING_CONFIG)
    if not isinstance(config, StudyConfiguration):
        st.session_state[_KEY_MAPPING_CONFIG] = StudyConfiguration(
            version="1.0.0",
            studyKey=study_key,
            reportingProfile="general",
        )
    else:
        config.study_key = study_key


def _go_to_step(step: int) -> None:
    st.session_state[_KEY_WIZARD_STEP] = max(1, min(len(_WIZARD_STEPS), step))


def _get_mapping_config() -> StudyConfiguration:
    return cast(StudyConfiguration, st.session_state[_KEY_MAPPING_CONFIG])


def _sanitise_study_key(study_key: str) -> str:
    safe_study_key = re.sub(r"[^a-z0-9_-]+", "_", study_key.lower()).strip("_")
    return safe_study_key or "study"


def _scan_schema(sdk: ImednetSDK, study_key: str) -> dict[str, Any]:
    loader = CachedRecordsLoader(sdk=sdk)
    records = loader.load_records(study_key)
    profiler = SchemaProfiler(sdk=sdk, loader=loader)
    profiles = profiler.profile_records(study_key, records=records)

    forms: list[dict[str, Any]] = []
    for profile in profiles.values():
        fields: list[dict[str, Any]] = []
        for field in profile.fields.values():
            fields.append(
                {
                    "variable_name": field.variable_name,
                    "label": field.label,
                    "population_rate": field.population_rate,
                    "inferred_type": field.inferred_type,
                    "unique_count": field.unique_count,
                    "unique_values": field.unique_values,
                }
            )
        forms.append(
            {
                "form_key": profile.form_key,
                "form_name": profile.form_name,
                "record_count": profile.record_count,
                "fields": fields,
            }
        )

    forms.sort(key=lambda form: cast(str, form["form_key"]))
    sample_records = []
    for record in records[:25]:
        sample_records.append(
            {
                "record_id": record.record_id,
                "form_key": record.form_key,
                "subject_key": record.subject_key,
                "record_data": record.record_data if isinstance(record.record_data, dict) else {},
            }
        )

    return {"forms": forms, "sample_records": sample_records}


def _schema() -> dict[str, Any]:
    discovered_schema = st.session_state.get(_KEY_DISCOVERED_SCHEMA)
    if isinstance(discovered_schema, dict):
        return discovered_schema
    return {"forms": [], "sample_records": []}


def _selected_forms(schema: dict[str, Any]) -> list[str]:
    selected = [
        st.session_state.get("wizard_target_form_ae"),
        st.session_state.get("wizard_target_form_pd"),
        st.session_state.get("wizard_target_form_dd"),
    ]
    selected_forms = [cast(str, value) for value in selected if isinstance(value, str) and value]
    if selected_forms:
        return sorted(set(selected_forms))
    return [cast(str, form["form_key"]) for form in schema.get("forms", [])]


def _field_candidates(schema: dict[str, Any], forms: list[str]) -> dict[str, list[str]]:
    by_form: dict[str, list[str]] = {}
    allowed_forms = set(forms)
    for form in schema.get("forms", []):
        form_key = cast(str, form["form_key"])
        if allowed_forms and form_key not in allowed_forms:
            continue
        candidates = [
            cast(str, field["variable_name"])
            for field in form.get("fields", [])
            if field.get("variable_name")
        ]
        by_form[form_key] = sorted(set(candidates))
    return by_form


def _existing_mapping_index(
    config: StudyConfiguration, domain: str, target_field: str
) -> MappingRule | None:
    for rule in config.mappings:
        if rule.domain == domain and rule.target_field == target_field:
            return rule
    return None


def _step_scan_and_profile(sdk: ImednetSDK, study_key: str) -> None:
    st.subheader("1. Scan & Profile Study Structure")
    st.markdown(
        "Discover forms, profile field populations, and choose source forms "
        "for AE, PD, and DD mapping."
    )

    if st.button("Scan and profile study", key="wizard_scan"):
        try:
            st.session_state[_KEY_DISCOVERED_SCHEMA] = _scan_schema(sdk, study_key)
            st.session_state[_KEY_VALIDATION_REPORT] = None
        except Exception as exc:  # pragma: no cover - defensive runtime UI handling
            st.error(f"Unable to profile study data ({type(exc).__name__}).")
            return
        st.success("Study structure scanned and profiled.")

    schema = _schema()
    forms = schema.get("forms", [])
    if not forms:
        st.info("Run scan to discover forms and field candidates.")
        return

    form_options = [cast(str, form["form_key"]) for form in forms]
    col_ae, col_pd, col_dd = st.columns(3)
    st.session_state["wizard_target_form_ae"] = col_ae.selectbox(
        "AE source form",
        options=form_options,
        key="wizard_target_form_ae",
    )
    st.session_state["wizard_target_form_pd"] = col_pd.selectbox(
        "PD source form",
        options=form_options,
        key="wizard_target_form_pd",
    )
    st.session_state["wizard_target_form_dd"] = col_dd.selectbox(
        "DD source form",
        options=form_options,
        key="wizard_target_form_dd",
    )

    st.dataframe(pd.DataFrame(forms), use_container_width=True)


def _step_field_mapping() -> None:
    st.subheader("2. Field Mapping")
    st.markdown(
        "Map canonical CDISC targets to discovered source variables using card-style mapping rows."
    )

    schema = _schema()
    selected_forms = _selected_forms(schema)
    candidates_by_form = _field_candidates(schema, selected_forms)
    if not candidates_by_form:
        st.info("No profiled forms available yet. Complete Step 1 first.")
        return

    config = _get_mapping_config()
    new_mappings: list[MappingRule] = []

    for domain, target_field, label in _CANONICAL_FIELDS:
        mapping_key = f"{domain}.{target_field}"
        existing = _existing_mapping_index(config, domain=domain, target_field=target_field)

        st.markdown(f"**{mapping_key}** — {label}")
        col_form, col_field, col_fallback = st.columns([2, 2, 1.5])

        form_options = ["", *selected_forms]
        selected_form = col_form.selectbox(
            "Source form",
            options=form_options,
            index=(
                form_options.index(existing.source_form_key)
                if existing and existing.source_form_key in form_options
                else 0
            ),
            key=f"wizard_map_form_{mapping_key}",
        )

        field_options = ["", *candidates_by_form.get(selected_form, [])]
        selected_field = col_field.selectbox(
            "Source field",
            options=field_options,
            index=(
                field_options.index(existing.source_variable_name)
                if existing and existing.source_variable_name in field_options
                else 0
            ),
            key=f"wizard_map_field_{mapping_key}",
        )

        fallback_value = col_fallback.text_input(
            "Fallback",
            value=existing.fallback_value or "" if existing else "",
            key=f"wizard_map_fallback_{mapping_key}",
        )

        if selected_form and selected_field:
            new_mappings.append(
                MappingRule(
                    domain=domain,
                    targetField=target_field,
                    sourceFormKey=selected_form,
                    sourceVariableName=selected_field,
                    fallbackValue=fallback_value or None,
                )
            )

    config.mappings = new_mappings
    st.session_state[_KEY_MAPPING_CONFIG] = config

    if config.mappings:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "domain": mapping.domain,
                        "target_field": mapping.target_field,
                        "source_form_key": mapping.source_form_key,
                        "source_variable_name": mapping.source_variable_name,
                    }
                    for mapping in config.mappings
                ]
            ),
            use_container_width=True,
        )


def _lookup_unique_values(
    schema: dict[str, Any], source_form_key: str, source_field: str
) -> list[str]:
    for form in schema.get("forms", []):
        if form.get("form_key") != source_form_key:
            continue
        for field in form.get("fields", []):
            if field.get("variable_name") == source_field:
                return [str(value) for value in field.get("unique_values", [])]
    return []


def _step_terminology() -> None:
    st.subheader("3. Categorical Terminology Normalization")
    st.markdown("Teach the system how raw categorical values should normalize to canonical values.")

    config = _get_mapping_config()
    if not config.mappings:
        st.info("Add field mappings first in Step 2.")
        return

    mapping_options = [f"{mapping.domain}.{mapping.target_field}" for mapping in config.mappings]
    selected_mapping = st.selectbox(
        "Mapped target field",
        options=mapping_options,
        key="wizard_terminology_mapping",
    )
    selected_rule = config.mappings[mapping_options.index(selected_mapping)]
    lookup_key = f"{selected_rule.domain}.{selected_rule.target_field}"
    unique_values = _lookup_unique_values(
        _schema(),
        source_form_key=selected_rule.source_form_key,
        source_field=selected_rule.source_variable_name,
    )

    current_lookup = dict(config.terminology_lookups.get(lookup_key, {}))
    updated_lookup: dict[str, str] = {}
    for raw_value in unique_values:
        normalized = st.text_input(
            f"{raw_value} →",
            value=current_lookup.get(raw_value, raw_value),
            key=f"wizard_norm_{lookup_key}_{raw_value}",
        ).strip()
        if normalized:
            updated_lookup[raw_value] = normalized
    config.terminology_lookups[lookup_key] = updated_lookup
    st.session_state[_KEY_MAPPING_CONFIG] = config

    col_clone, col_undo, col_reset = st.columns(3)
    if col_clone.button("Clone configuration snapshot", key="wizard_clone_snapshot"):
        snapshots = cast(list[dict[str, Any]], st.session_state[_KEY_HISTORY])
        snapshots.append(config.model_dump(mode="json", by_alias=True))
        st.success("Configuration snapshot saved.")
    if col_undo.button("Undo last snapshot", key="wizard_undo_snapshot"):
        snapshots = cast(list[dict[str, Any]], st.session_state[_KEY_HISTORY])
        if snapshots:
            st.session_state[_KEY_MAPPING_CONFIG] = StudyConfiguration.from_json(snapshots.pop())
            st.success("Reverted to previous configuration snapshot.")
        else:
            st.warning("No snapshots available to undo.")
    if col_reset.button("Reset normalizations", key="wizard_reset_normalizations"):
        config = _get_mapping_config()
        config.terminology_lookups = {}
        st.session_state[_KEY_MAPPING_CONFIG] = config
        st.success("Terminology normalizations reset.")


def _apply_lookup(config: StudyConfiguration, lookup_key: str, value: Any) -> Any:
    if isinstance(value, str):
        return config.terminology_lookups.get(lookup_key, {}).get(value, value)
    return value


def _build_preview_rows(
    config: StudyConfiguration, sample_records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in sample_records:
        row: dict[str, Any] = {
            "record_id": record.get("record_id"),
            "form_key": record.get("form_key"),
            "subject_key": record.get("subject_key"),
        }
        record_data = (
            record.get("record_data") if isinstance(record.get("record_data"), dict) else {}
        )
        for mapping in config.mappings:
            if mapping.source_form_key != record.get("form_key"):
                continue
            source_value = mapping.fallback_value
            if isinstance(record_data, dict):
                source_value = record_data.get(mapping.source_variable_name, mapping.fallback_value)
            lookup_key = f"{mapping.domain}.{mapping.target_field}"
            row[lookup_key] = _apply_lookup(config, lookup_key, source_value)
        rows.append(row)
    return rows


def _step_preview_and_layout() -> None:
    st.subheader("4. Layout & Visual Configuration")
    st.markdown("Configure dashboard widgets and preview mapped values for the first five records.")

    config = _get_mapping_config()
    if not config.mappings:
        st.info("Create mappings in Step 2 before previewing.")
        return

    default_types = [widget.type for widget in config.widgets if widget.type in _WIDGET_TYPES] or [
        "kpi_card",
        "bar_chart",
    ]
    selected_widgets = st.multiselect(
        "Widget types",
        options=list(_WIDGET_TYPES),
        default=default_types,
        key="wizard_widget_types",
    )
    layout_cols = st.slider("Widget column width", min_value=3, max_value=12, value=6, step=1)
    config.widgets = [
        WidgetConfig(
            widgetId=f"widget-{index + 1}",
            type=widget_type,
            title=f"{widget_type.replace('_', ' ').title()}",
            domain=config.mappings[0].domain,
            xAxis=None,
            yAxis=None,
            layoutCols=layout_cols,
        )
        for index, widget_type in enumerate(selected_widgets)
    ]
    st.session_state[_KEY_MAPPING_CONFIG] = config

    sample_records = cast(list[dict[str, Any]], _schema().get("sample_records", []))[:5]
    preview_rows = _build_preview_rows(config, sample_records)
    report = {
        "mapped_fields": len(config.mappings),
        "terminology_rules": sum(len(mapping) for mapping in config.terminology_lookups.values()),
        "preview_rows": len(preview_rows),
        "unmapped_canonical_fields": len(_CANONICAL_FIELDS) - len(config.mappings),
    }
    st.session_state[_KEY_VALIDATION_REPORT] = report

    metrics = st.columns(4)
    metrics[0].metric("Mapped Fields", report["mapped_fields"])
    metrics[1].metric("Terminology Rules", report["terminology_rules"])
    metrics[2].metric("Preview Rows", report["preview_rows"])
    metrics[3].metric("Unmapped Canonical", report["unmapped_canonical_fields"])

    if preview_rows:
        st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)
    else:
        st.info("No sample records available to preview.")


def _step_export(study_key: str) -> None:
    st.subheader("5. Export / Save")
    st.markdown("Download or persist the finalized StudyConfiguration JSON.")

    config = _get_mapping_config()
    payload = json.dumps(config.model_dump(mode="json", by_alias=True), indent=2)

    st.json(json.loads(payload))
    st.download_button(
        label="Download StudyConfiguration JSON",
        data=payload,
        file_name=f"{study_key.lower()}_study_configuration.json",
        mime="application/json",
    )

    if st.button("Save configuration locally", key="wizard_save_local"):
        try:
            output_dir = Path.cwd() / ".imednet" / "configs"
            output_dir.mkdir(parents=True, exist_ok=True)
            safe_study_key = _sanitise_study_key(study_key)
            output_file = output_dir / f"{safe_study_key}_study_configuration.json"
            output_file.write_text(payload, encoding="utf-8")
        except OSError:  # pragma: no cover - defensive runtime UI handling
            st.error("Unable to save configuration locally.")
            return
        st.success(f"Saved to {output_file}")


def render_page() -> None:
    st.title("🧭 Study Setup Wizard")
    with st.expander("UX Design Specification", expanded=False):
        _render_design_specification()

    if not st.session_state.get("_imednet_connected"):
        st.info("Please connect from the sidebar to configure and publish a study mapping.")
        return

    try:
        sdk = get_sdk()
        study_key = get_study_key()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    _initialise_state(study_key)
    current_step = int(st.session_state[_KEY_WIZARD_STEP])

    st.caption(f"Step {current_step} of {len(_WIZARD_STEPS)} — {_WIZARD_STEPS[current_step - 1]}")
    st.progress(current_step / len(_WIZARD_STEPS))

    nav_columns = st.columns(len(_WIZARD_STEPS))
    for index, title in enumerate(_WIZARD_STEPS, start=1):
        if nav_columns[index - 1].button(
            f"{index}. {title.split(' ')[0]}",
            key=f"wizard_nav_{index}",
            use_container_width=True,
        ):
            _go_to_step(index)

    current_step = int(st.session_state[_KEY_WIZARD_STEP])
    if current_step == 1:
        _step_scan_and_profile(sdk, study_key)
    elif current_step == 2:
        _step_field_mapping()
    elif current_step == 3:
        _step_terminology()
    elif current_step == 4:
        _step_preview_and_layout()
    else:
        _step_export(study_key)

    prev_col, next_col = st.columns(2)
    if prev_col.button("← Previous", key="wizard_prev", disabled=current_step <= 1):
        _go_to_step(current_step - 1)

    disable_next = current_step == 1 and not _schema().get("forms")
    if next_col.button(
        "Next →",
        key="wizard_next",
        disabled=current_step >= len(_WIZARD_STEPS) or disable_next,
    ):
        _go_to_step(current_step + 1)


render_page()
