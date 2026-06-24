"""TODO: Add docstring."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .paginated_grid import paginated_slice


def filterable_dataframe(df: pd.DataFrame, key: str, height: int = 400) -> None:
    """Render a searchable and paginated dataframe.

    Args:
        df: Source DataFrame to display.
        key: Unique key namespace used for filter and pagination widgets.
        height: Height in pixels passed to ``st.dataframe``.
    """
    query = st.text_input("🔍 Filter rows", key=f"filter_{key}")
    if query:
        mask = df.apply(lambda col: col.astype(str).str.contains(query, case=False, na=False))
        df = df[mask.any(axis=1)]
    page_df = paginated_slice(df, key=key)
    st.dataframe(page_df, use_container_width=True, height=height)
