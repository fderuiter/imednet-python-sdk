from __future__ import annotations

from typing import Any

import pandas as pd

from imednet.spi.security import mask_clinical_phi as redact_sensitive_payload


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
