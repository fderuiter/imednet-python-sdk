"""Data Lineage components.

Provides utilities for redacting sensitive fields and rendering multi-pane
views that trace the transformation of raw EDC records into canonical models.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def render_lineage_panes(
    *,
    raw_record: dict[str, Any] | None,
    mapping_rules: list[dict[str, Any]],
    canonical_payload: dict[str, Any],
) -> None:
    """Render side-by-side lineage panes for raw, mapping, and canonical views."""
    # Import inside function so tests can patch `streamlit` via sys.modules.
    import streamlit as st

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Raw EDC Payload")
        if raw_record:
            st.json(_redact_sensitive_keys(raw_record))
        else:
            st.info("Raw record context unavailable.")
    with c2:
        st.subheader("Transformation Matrix")
        if mapping_rules:
            st.dataframe(pd.DataFrame(mapping_rules), use_container_width=True)
        else:
            st.info("Direct passthrough (No translation required).")
    with c3:
        st.subheader("Canonical Target")
        st.json(_redact_sensitive_keys(canonical_payload))


def _redact_sensitive_keys(data: dict[str, Any]) -> dict[str, Any]:
    """Redact standard sensitive keys from payloads for secure display."""
    sensitive_keys = {"patient_name", "ssn", "dob", "mrn"}
    redacted: dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in sensitive_keys:
            redacted[k] = "***MASKED***"
        elif isinstance(v, dict):
            redacted[k] = _redact_sensitive_keys(v)
        else:
            redacted[k] = v
    return redacted
