from __future__ import annotations

from typing import Any

import pandas as pd

_SENSITIVE_PATTERNS = frozenset(
    {
        "password",
        "token",
        "secret",
        "credential",
        "api_key",
        "apikey",
        "auth_key",
        "access_key",
        "security_key",
        "private_key",
        "client_secret",
    }
)
_REDACTION_MARKER = "***REDACTED***"


def redact_sensitive_payload(data: Any) -> Any:
    """Return *data* with sensitive key values redacted."""
    if isinstance(data, dict):
        redacted: dict[str, Any] = {}
        for key, value in data.items():
            key_str = str(key)
            key_lower = key_str.lower()
            if any(pattern in key_lower for pattern in _SENSITIVE_PATTERNS):
                redacted[key_str] = _REDACTION_MARKER
            else:
                redacted[key_str] = redact_sensitive_payload(value)
        return redacted

    if isinstance(data, list):
        return [redact_sensitive_payload(item) for item in data]

    if isinstance(data, tuple):
        return tuple(redact_sensitive_payload(item) for item in data)

    return data


def render_lineage_panes(
    *,
    raw_record: dict[str, Any] | None,
    mapping_rules: list[dict[str, Any]],
    canonical_payload: dict[str, Any],
) -> None:
    """Render side-by-side lineage panes for raw, mapping, and canonical views."""
    # Import inside function so tests can patch `streamlit` via sys.modules.
    import streamlit as st

    left_pane, mid_pane, right_pane = st.columns(3)

    with left_pane:
        st.markdown("**📥 Raw EDC Record**")
        if raw_record is not None:
            st.json(raw_record)
        else:
            st.info("Raw record not available (no matching source form configured).")

    with mid_pane:
        st.markdown("**⚙️ Applied Mapping Rules**")
        if mapping_rules:
            st.dataframe(pd.DataFrame(mapping_rules), use_container_width=True)
        else:
            st.info("No mapping rules configured for this domain.")

    with right_pane:
        st.markdown("**📤 Canonical Model**")
        st.json(canonical_payload)
