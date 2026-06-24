"""Data Lineage Explorer — drill-down from aggregated metrics to raw source records.

Provides an interactive drill-down path from dashboard metric values to the
underlying canonical models and, ultimately, to the raw EDC record payload.
No credentials are exposed in the rendered view.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from imednet.spi.models import AdverseEvent, DeviceDeficiency, ProtocolDeviation, StudyConfiguration
from imednet_streamlit.auth import get_sdk, get_study_key
from imednet_streamlit.components import redact_sensitive_payload, render_lineage_panes
from imednet_workflows import CachedRecordsLoader
from imednet_workflows.extraction_engine import ExtractionResult, extract_canonical_records

# ---------------------------------------------------------------------------
# Session-state keys
# ---------------------------------------------------------------------------
_KEY_CONNECTED = "_imednet_connected"
_KEY_RECORDS = "_lineage_records"
_KEY_EXTRACTION = "_lineage_extraction"
_KEY_CONFIG = "_lineage_config"
_KEY_SELECTED_DOMAIN = "_lineage_domain"
_KEY_SELECTED_IDX = "_lineage_selected_idx"

_DOMAIN_LABELS = {
    "AE": "Adverse Events",
    "PD": "Protocol Deviations",
    "DD": "Device Deficiencies",
}


def _load_data(study_key: str) -> None:
    """Fetch records from cache and run extraction."""
    sdk = get_sdk()
    loader = CachedRecordsLoader(sdk=sdk)
    records = loader.load_records(study_key)
    st.session_state[_KEY_RECORDS] = records

    config: StudyConfiguration | None = st.session_state.get(_KEY_CONFIG)
    if not isinstance(config, StudyConfiguration):
        config = StudyConfiguration(
            version="1.0.0",
            studyKey=study_key,
            reportingProfile="general",
        )

    extraction = extract_canonical_records(records, config)
    st.session_state[_KEY_EXTRACTION] = extraction


def _get_domain_models(
    extraction: ExtractionResult, domain: str
) -> list[AdverseEvent | ProtocolDeviation | DeviceDeficiency]:
    """TODO: Add docstring."""
    if domain == "AE":
        return list(extraction.adverse_events)
    if domain == "PD":
        return list(extraction.protocol_deviations)
    return list(extraction.device_deficiencies)


def _models_to_frame(
    models: list[Any],
) -> pd.DataFrame:
    """TODO: Add docstring."""
    if not models:
        return pd.DataFrame()
    rows = [m.model_dump(mode="python", by_alias=False) for m in models]
    return pd.DataFrame(rows)


def _render_metric_summary(extraction: ExtractionResult) -> str | None:
    """Render clickable metric tiles and return the selected domain."""
    st.subheader("📊 Metric Overview")
    st.markdown("Click a metric tile to drill down to the underlying records.")

    counts = {
        "AE": len(extraction.adverse_events),
        "PD": len(extraction.protocol_deviations),
        "DD": len(extraction.device_deficiencies),
    }

    cols = st.columns(3)
    selected_domain: str | None = st.session_state.get(_KEY_SELECTED_DOMAIN)

    for idx, (domain, count) in enumerate(counts.items()):
        label = _DOMAIN_LABELS[domain]
        cols[idx].metric(label, count)
        btn_key = f"lineage_drill_{domain}"
        if cols[idx].button(f"Drill into {domain}", key=btn_key):
            selected_domain = domain
            st.session_state[_KEY_SELECTED_DOMAIN] = domain
            st.session_state[_KEY_SELECTED_IDX] = None

    return selected_domain


def _render_record_table(
    models: list[Any],
    domain: str,
) -> int | None:
    """Render the canonical records table and return the selected row index."""
    st.subheader(f"📋 {_DOMAIN_LABELS.get(domain, domain)} Records")
    if not models:
        st.info(f"No {domain} records found.")
        return None

    df = _models_to_frame(models)
    st.dataframe(df, use_container_width=True)

    total = len(models)
    selected_idx: int | None = st.session_state.get(_KEY_SELECTED_IDX)

    col_input, col_btn = st.columns([3, 1])
    raw_val = col_input.text_input(
        "Record index (0-based) for lineage trace",
        value=str(selected_idx) if selected_idx is not None else "0",
        key="lineage_idx_input",
    )
    if col_btn.button("Trace lineage", key="lineage_trace_btn"):
        try:
            idx = int(raw_val)
            if 0 <= idx < total:
                st.session_state[_KEY_SELECTED_IDX] = idx
                selected_idx = idx
            else:
                st.warning(f"Index must be between 0 and {total - 1}.")
        except ValueError:
            st.warning("Please enter a valid integer index.")

    return selected_idx


def _find_raw_record(
    study_key: str,
    domain: str,
    model_idx: int,
    extraction: ExtractionResult,
) -> dict[str, Any] | None:
    """Return the raw EDC record dict that produced the canonical model at *model_idx*."""
    # Build a simple lookup: raw records keyed by record_id
    raw_records = st.session_state.get(_KEY_RECORDS, [])
    config: StudyConfiguration | None = st.session_state.get(_KEY_CONFIG)
    if not isinstance(config, StudyConfiguration):
        return None

    models = _get_domain_models(extraction, domain)
    if model_idx >= len(models):
        return None

    canonical_model = models[model_idx]
    subject_key = getattr(canonical_model, "subject_key", None)

    # Find the first raw record for this subject that matches a form mapped in config
    mapped_forms = {rule.source_form_key for rule in config.mappings if rule.domain == domain}
    for raw in raw_records:
        raw_form = getattr(raw, "form_key", None)
        raw_subject = getattr(raw, "subject_key", None)
        if raw_form in mapped_forms and raw_subject == subject_key:
            return {
                "record_id": getattr(raw, "record_id", None),
                "form_key": raw_form,
                "subject_key": raw_subject,
                "record_data": _redact_sensitive(getattr(raw, "record_data", {}) or {}),
            }
    return None


def _find_mapping_rules(domain: str) -> list[dict[str, Any]]:
    """Return a list of mapping rule dicts for the given domain."""
    config: StudyConfiguration | None = st.session_state.get(_KEY_CONFIG)
    if not isinstance(config, StudyConfiguration):
        return []
    return [
        {
            "domain": rule.domain,
            "target_field": rule.target_field,
            "source_form_key": rule.source_form_key,
            "source_variable_name": rule.source_variable_name,
            "fallback_value": rule.fallback_value,
        }
        for rule in config.mappings
        if rule.domain == domain
    ]


def _redact_sensitive(data: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *data* with common sensitive keys redacted."""
    return redact_sensitive_payload(data)


def _render_lineage_trace(
    domain: str,
    model_idx: int,
    extraction: ExtractionResult,
    study_key: str,
) -> None:
    """Render the side-by-side three-pane lineage trace for a single record."""
    st.subheader(f"🔎 Lineage Trace — {_DOMAIN_LABELS.get(domain, domain)} record [{model_idx}]")

    models = _get_domain_models(extraction, domain)
    if model_idx >= len(models):
        st.warning("Record index is out of range.")
        return

    canonical_model = models[model_idx]
    raw_record = _find_raw_record(study_key, domain, model_idx, extraction)
    mapping_rules = _find_mapping_rules(domain)

    render_lineage_panes(
        raw_record=raw_record,
        mapping_rules=mapping_rules,
        canonical_payload=canonical_model.model_dump(mode="python", by_alias=False),
    )


def _render_config_input() -> None:
    """Allow the user to paste a StudyConfiguration JSON to drive mapping."""
    with st.expander("⚙️ Load StudyConfiguration (optional)", expanded=False):
        st.markdown(
            "Paste a StudyConfiguration JSON to enable mapped-field lineage traces. "
            "Without a configuration, only the raw canonical extraction is shown."
        )
        raw_json = st.text_area(
            "StudyConfiguration JSON",
            value="",
            height=200,
            key="lineage_config_json",
        )
        if st.button("Apply configuration", key="lineage_apply_config"):
            if raw_json.strip():
                try:
                    config = StudyConfiguration.model_validate_json(raw_json)
                    st.session_state[_KEY_CONFIG] = config
                    st.success("Configuration loaded.")
                except Exception as exc:  # pragma: no cover - defensive runtime UI handling
                    st.error(f"Invalid StudyConfiguration JSON ({type(exc).__name__}): {exc}")
            else:
                st.session_state.pop(_KEY_CONFIG, None)
                st.success("Configuration cleared.")


def render_page() -> None:
    """TODO: Add docstring."""
    st.title("🔭 Data Lineage Explorer")

    if not st.session_state.get(_KEY_CONNECTED):
        st.info("Please connect from the sidebar to explore data lineage.")
        return

    try:
        study_key = get_study_key()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    _render_config_input()

    if st.button("Load / Refresh records", key="lineage_load_btn"):
        try:
            _load_data(study_key)
            st.success("Records loaded.")
        except Exception as exc:  # pragma: no cover - defensive runtime UI handling
            st.error(f"Unable to load records ({type(exc).__name__}): {exc}")
            return

    extraction: ExtractionResult | None = st.session_state.get(_KEY_EXTRACTION)
    if not isinstance(extraction, ExtractionResult):
        st.info("Click **Load / Refresh records** to begin.")
        return

    st.divider()
    selected_domain = _render_metric_summary(extraction)

    if selected_domain is None:
        return

    st.divider()
    models = _get_domain_models(extraction, selected_domain)
    selected_idx = _render_record_table(models, selected_domain)

    if selected_idx is not None:
        st.divider()
        _render_lineage_trace(selected_domain, selected_idx, extraction, study_key)


render_page()
