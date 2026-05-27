from __future__ import annotations

from math import ceil

import pandas as pd
import streamlit as st


def paginated_slice(
    df: pd.DataFrame,
    *,
    key: str,
    page_size_options: tuple[int, ...] = (50, 100, 200),
    default_page_size: int = 100,
) -> pd.DataFrame:
    """Render pager controls and return the current page slice."""
    if default_page_size not in page_size_options:
        page_size_options = tuple(sorted(set((*page_size_options, default_page_size))))

    page_size = st.selectbox(
        "Rows per page",
        options=page_size_options,
        index=page_size_options.index(default_page_size),
        key=f"{key}_page_size",
    )
    total_rows = len(df)
    total_pages = max(1, ceil(total_rows / page_size))

    if f"{key}_page" not in st.session_state:
        st.session_state[f"{key}_page"] = 1
    current_page = st.session_state[f"{key}_page"]
    clamped_page = min(max(1, current_page), total_pages)
    if clamped_page != current_page:
        st.session_state[f"{key}_page"] = clamped_page

    col_prev, col_info, col_next = st.columns([1, 2, 1])
    if col_prev.button(
        "Previous", key=f"{key}_prev", disabled=st.session_state[f"{key}_page"] <= 1
    ):
        st.session_state[f"{key}_page"] -= 1
    if col_next.button(
        "Next",
        key=f"{key}_next",
        disabled=st.session_state[f"{key}_page"] >= total_pages,
    ):
        st.session_state[f"{key}_page"] += 1
    page = st.session_state[f"{key}_page"]
    start = (page - 1) * page_size
    end = min(start + page_size, total_rows)
    start_display = start + 1 if total_rows else 0
    col_info.caption(
        f"Page {page} of {total_pages} • Showing {start_display}-{end} of {total_rows}"
    )

    return df.iloc[start:end]


def top_n_with_other(
    df: pd.DataFrame,
    *,
    label_column: str,
    value_column: str,
    top_n: int = 10,
    other_label: str = "Other",
) -> pd.DataFrame:
    """Return top-N rows plus an aggregated 'Other' row."""
    if df.empty:
        return df

    sorted_df = df.sort_values(value_column, ascending=False).reset_index(drop=True)
    top_df = sorted_df.head(top_n).copy()
    remainder = sorted_df.iloc[top_n:]
    if remainder.empty:
        return top_df

    other_value = remainder[value_column].sum()
    if other_value <= 0:
        return top_df

    other_row = pd.DataFrame([{label_column: other_label, value_column: other_value}])
    return pd.concat([top_df, other_row], ignore_index=True)
