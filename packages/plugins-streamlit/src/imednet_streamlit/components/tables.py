from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from .paginated_grid import paginated_slice


def apply_enrichment_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """Mask sensitive fields and apply study-specific enrichment rules."""
    from imednet.utils.security import global_sensitivity_registry

    if df.empty:
        return df

    df = df.copy()

    # Apply global sensitivity registry masking
    sensitive_cols = [
        col for col in df.columns if global_sensitivity_registry.is_sensitive(str(col))
    ]
    for col in sensitive_cols:
        df[col] = "***MASKED***"

    # Try to apply study-specific EnrichmentPipeline
    try:
        from imednet_streamlit.auth import get_study_key

        study_key = get_study_key()
    except RuntimeError:
        return df

    try:
        from imednet.integrations.enrichment import EnrichmentPipeline
        from imednet_workflows.config_version_control import ConfigVersionStore

        store = ConfigVersionStore()
        history = store.get_history(study_key)
        if history:
            latest_commit = history[-1]["commit_id"]
            config = store.rollback_config(study_key, latest_commit)
            pipeline = EnrichmentPipeline(config)

            records = df.where(pd.notnull(df), None).to_dict(orient="records")
            records = pipeline.process(records)
            df = pd.DataFrame(records)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not apply EnrichmentPipeline: {e}")

    return df


def filterable_dataframe(df: pd.DataFrame, key: str, height: int = 400) -> None:
    """Render a searchable and paginated dataframe.

    Args:
        df: Source DataFrame to display.
        key: Unique key namespace used for filter and pagination widgets.
        height: Height in pixels passed to ``st.dataframe``.
    """
    df = apply_enrichment_to_df(df)

    query = st.text_input("🔍 Filter rows", key=f"filter_{key}")
    if query:
        mask = df.apply(lambda col: col.astype(str).str.contains(query, case=False, na=False))
        df = df[mask.any(axis=1)]
    page_df = paginated_slice(df, key=key)
    st.dataframe(page_df, use_container_width=True, height=height)
