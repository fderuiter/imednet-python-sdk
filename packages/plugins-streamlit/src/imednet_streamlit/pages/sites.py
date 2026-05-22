from __future__ import annotations

import pandas as pd
import streamlit as st

from imednet_streamlit import components
from imednet_streamlit.auth import get_sdk, get_study_key

_HIGH_QUERY_RATE_THRESHOLD = 20.0
_HIGH_RATE_COLOR = "#ffe0e0"


@st.cache_data(ttl=600, show_spinner=False)
def _fetch_site_metrics(_sdk: object, study_key: str) -> pd.DataFrame:
    """Joins subjects + queries to produce a per-site metrics DataFrame."""
    from imednet_workflows.query_management import QueryManagementWorkflow

    # --- Subjects ---
    subjects = _sdk.subjects.list(study_key=study_key)  # type: ignore[attr-defined]
    df_subjects = pd.DataFrame(
        [
            {
                "subject_key": s.subject_key,
                "site_name": s.site_name,
                "deleted": s.deleted,
            }
            for s in subjects
        ]
    )
    _subject_cols = ["subject_key", "site_name", "deleted"]
    if df_subjects.empty:
        df_subjects = pd.DataFrame(columns=_subject_cols)
    else:
        df_subjects = df_subjects[~df_subjects["deleted"]]

    site_enrollment = df_subjects.groupby("site_name").size().reset_index(name="enrolled_count")

    # --- Open Queries ---
    workflow = QueryManagementWorkflow(sdk=_sdk)  # type: ignore[arg-type]
    open_queries = workflow.get_open_queries(study_key=study_key)
    df_queries = pd.DataFrame(
        [
            {
                "subject_key": q.subject_key,
                "annotation_id": q.annotation_id,
                "date_created": q.date_created,
            }
            for q in open_queries
        ]
    )
    _query_cols = ["subject_key", "annotation_id", "date_created"]
    if df_queries.empty:
        df_queries = pd.DataFrame(columns=_query_cols)

    # Join queries → subjects → site_name
    df_q_with_site = df_queries.merge(
        df_subjects[["subject_key", "site_name"]], on="subject_key", how="left"
    )

    if df_q_with_site.empty:
        site_queries = pd.DataFrame(columns=["site_name", "open_queries", "avg_days_open"])
    else:
        site_queries = (
            df_q_with_site.groupby("site_name")
            .agg(
                open_queries=("annotation_id", "count"),
                avg_days_open=(
                    "date_created",
                    lambda x: (
                        pd.Timestamp.now(tz="UTC") - pd.to_datetime(x, utc=True)
                    ).dt.days.mean(),
                ),
            )
            .reset_index()
        )

    # Merge enrollment + queries
    df_metrics = site_enrollment.merge(site_queries, on="site_name", how="left").fillna(0)
    for col in ("enrolled_count", "open_queries", "avg_days_open"):
        df_metrics[col] = pd.to_numeric(df_metrics[col], errors="coerce").fillna(0)
    df_metrics["query_rate"] = (
        df_metrics["open_queries"] / df_metrics["enrolled_count"].replace(0, 1) * 100
    ).round(1)
    return df_metrics


def _highlight_high_rate(val: float) -> str:
    return f"background-color: {_HIGH_RATE_COLOR}" if val > _HIGH_QUERY_RATE_THRESHOLD else ""


st.title("🏥 Site Performance")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

sdk = get_sdk()
study_key = get_study_key()
df_metrics = _fetch_site_metrics(sdk, study_key)

# ── KPI Row ───────────────────────────────────────────────────────────────
total_sites = int(df_metrics["site_name"].nunique()) if not df_metrics.empty else 0
total_enrolled = int(df_metrics["enrolled_count"].sum()) if not df_metrics.empty else 0
total_open_queries = int(df_metrics["open_queries"].sum()) if not df_metrics.empty else 0
avg_query_rate = round(float(df_metrics["query_rate"].mean()), 1) if not df_metrics.empty else 0.0

components.kpi_row(
    [
        {"label": "Total Sites", "value": total_sites},
        {"label": "Total Enrolled", "value": total_enrolled},
        {"label": "Total Open Queries", "value": total_open_queries},
        {"label": "Avg Query Rate %", "value": f"{avg_query_rate}%"},
    ]
)

# ── Two-column charts ─────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Enrollment & Open Queries by Site")
    if not df_metrics.empty:
        chart_df = df_metrics[["site_name", "enrolled_count", "open_queries"]].melt(
            id_vars="site_name",
            value_vars=["enrolled_count", "open_queries"],
            var_name="metric",
            value_name="count",
        )
        st.altair_chart(
            components.bar_chart(
                chart_df,
                x="count",
                y="site_name",
                color="metric",
                title="Enrolled Subjects & Open Queries per Site",
            ),
            use_container_width=True,
        )

with col_right:
    st.subheader("Avg Days Open by Site")
    if not df_metrics.empty:
        days_df = df_metrics[["site_name", "avg_days_open"]].copy()
        st.altair_chart(
            components.bar_chart(
                days_df,
                x="avg_days_open",
                y="site_name",
                title="Average Days Open per Site",
            ),
            use_container_width=True,
        )

# ── Per-site metrics table ────────────────────────────────────────────────
st.subheader("Per-Site Metrics")
display_cols = ["site_name", "enrolled_count", "open_queries", "query_rate", "avg_days_open"]
if not df_metrics.empty:
    df_display = df_metrics[display_cols].copy()
else:
    df_display = pd.DataFrame(columns=display_cols)

styled = df_display.style.map(_highlight_high_rate, subset=["query_rate"])
st.dataframe(styled, use_container_width=True)

components.csv_download_button(df_display, filename="site_metrics.csv")
