from __future__ import annotations

import pandas as pd
import streamlit as st

from imednet_streamlit import components
from imednet_streamlit.auth import get_sdk, get_study_key


@st.cache_data(ttl=600, show_spinner=False)
def _fetch_queries(_sdk: object, study_key: str) -> pd.DataFrame:
    """Fetches all queries and returns a normalized DataFrame."""
    from imednet_workflows.query_management import QueryManagementWorkflow

    workflow = QueryManagementWorkflow(sdk=_sdk)  # type: ignore[arg-type]
    open_q = workflow.get_open_queries(study_key=study_key)
    all_q = _sdk.queries.list(study_key=study_key)  # type: ignore[attr-defined]
    open_ids = {q.annotation_id for q in open_q}
    rows = []
    for q in all_q:
        rows.append(
            {
                "annotation_id": q.annotation_id,
                "subject_key": q.subject_key,
                "variable": q.variable,
                "annotation_type": q.annotation_type,
                "description": q.description,
                "date_created": q.date_created,
                "date_modified": q.date_modified,
                "status": "Open" if q.annotation_id in open_ids else "Closed",
            }
        )
    _columns = [
        "annotation_id",
        "subject_key",
        "variable",
        "annotation_type",
        "description",
        "date_created",
        "date_modified",
        "status",
    ]
    if not rows:
        return pd.DataFrame(columns=_columns)
    return pd.DataFrame(rows)


st.title("🔍 Query Status Overview")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

sdk = get_sdk()
study_key = get_study_key()
df = _fetch_queries(sdk, study_key)

# ── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.subheader("Filters")
    status_filter: list[str] = st.multiselect(
        "Status", ["Open", "Closed"], default=["Open", "Closed"]
    )
    type_options = df["annotation_type"].dropna().unique().tolist() if not df.empty else []
    type_filter: list[str] = st.multiselect("Annotation Type", type_options)

    if not df.empty and pd.api.types.is_datetime64_any_dtype(df["date_created"]):
        min_date = df["date_created"].min().date()
        max_date = df["date_created"].max().date()
    else:
        from datetime import date as _date

        min_date = _date.today()
        max_date = _date.today()
    date_range = st.date_input("Date Range", value=[min_date, max_date])

# ── Apply filters ─────────────────────────────────────────────────────────
df_filtered = df.copy()
if status_filter:
    df_filtered = df_filtered[df_filtered["status"].isin(status_filter)]
if type_filter:
    df_filtered = df_filtered[df_filtered["annotation_type"].isin(type_filter)]
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
    if not df_filtered.empty and pd.api.types.is_datetime64_any_dtype(
        df_filtered["date_created"]
    ):
        df_filtered = df_filtered[
            (df_filtered["date_created"].dt.date >= start_date)
            & (df_filtered["date_created"].dt.date <= end_date)
        ]

# ── KPI Row ───────────────────────────────────────────────────────────────
total = len(df_filtered)
open_count = int((df_filtered["status"] == "Open").sum()) if not df_filtered.empty else 0
closed_count = int((df_filtered["status"] == "Closed").sum()) if not df_filtered.empty else 0
open_pct = f"{open_count / total * 100:.1f}%" if total > 0 else "N/A"

components.kpi_row(
    [
        {"label": "Total Queries", "value": total},
        {"label": "Open Queries", "value": open_count},
        {"label": "Closed Queries", "value": closed_count},
        {"label": "Open %", "value": open_pct},
    ]
)

# ── Two-column charts ─────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Queries by Status")
    if not df_filtered.empty:
        status_counts = df_filtered.groupby("status").size().reset_index(name="count")
        st.altair_chart(
            components.bar_chart(status_counts, x="count", y="status", title="Status Breakdown"),
            use_container_width=True,
        )

with col_right:
    st.subheader("Top 10 Variables")
    if not df_filtered.empty:
        var_counts = (
            df_filtered.groupby("variable").size().reset_index(name="count").nlargest(10, "count")
        )
        st.altair_chart(
            components.bar_chart(var_counts, x="count", y="variable", title="Top Variables"),
            use_container_width=True,
        )

# ── Trend line chart ───────────────────────────────────────────────────────
st.subheader("Query Trend (by Day)")
if not df_filtered.empty and pd.api.types.is_datetime64_any_dtype(df_filtered["date_created"]):
    trend_df = df_filtered.copy()
    trend_df["date"] = trend_df["date_created"].dt.normalize()
    trend_agg = trend_df.groupby(["date", "status"]).size().reset_index(name="count")
    st.altair_chart(
        components.line_chart(
            trend_agg,
            x="date",
            y="count",
            color="status",
            title="Queries Opened per Day",
        ),
        use_container_width=True,
    )

# ── Data table and downloads ──────────────────────────────────────────────
st.subheader("All Queries")
components.filterable_dataframe(df_filtered, key="queries_table")

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    components.csv_download_button(df_filtered, filename="queries.csv")
with col_dl2:
    components.excel_download_button(df_filtered, filename="queries.xlsx")
