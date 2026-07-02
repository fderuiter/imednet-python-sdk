"""Subject enrollment dashboard.

Visualizes subject registration trends over time and enrollment status
distribution across the study.
"""

from __future__ import annotations

from datetime import date as _date

import pandas as pd
import streamlit as st

from imednet_streamlit import components
from imednet_streamlit.auth import get_sdk, get_study_key
from imednet_streamlit.components.charts import render_accessible_chart


@st.cache_data(ttl=600, show_spinner=False)
def _fetch_subjects(_sdk: object, study_key: str) -> pd.DataFrame:
    """Fetches all subjects and returns a normalized DataFrame (deleted excluded)."""
    from imednet.spi.models import Record, Site, Subject, Query

    subjects = _sdk.get_subjects(study_key=study_key)  # type: ignore[attr-defined]
    fields = list(Subject.model_fields.keys())

    rows = []
    for s in subjects:
        row = {f: getattr(s, f, None) for f in fields}
        rows.append(row)

    if not rows:
        return pd.DataFrame(columns=fields)
    df = pd.DataFrame(rows)
    return df[~df["deleted"]]


@st.cache_data(ttl=600, show_spinner=False)
def _fetch_sites(_sdk: object, study_key: str) -> pd.DataFrame:
    """Fetches all sites and returns a normalized DataFrame."""
    sites = _sdk.get_sites(study_key=study_key)  # type: ignore[attr-defined]
    if not sites:
        return pd.DataFrame()
    return pd.DataFrame([s.model_dump() for s in sites])


# ── Page header ───────────────────────────────────────────────────────────────
st.title("👥 Subject Enrollment Overview")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

sdk = get_sdk()
study_key = get_study_key()
df = _fetch_subjects(sdk, study_key)

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.subheader("Filters")

    site_options = df["site_name"].dropna().unique().tolist() if not df.empty else []
    site_filter: list[str] = st.multiselect("Site", site_options)

    status_options = df["subject_status"].dropna().unique().tolist() if not df.empty else []
    status_filter: list[str] = st.multiselect("Subject Status", status_options)

    if not df.empty and pd.api.types.is_datetime64_any_dtype(df["enrollment_start_date"]):
        valid_dates = df["enrollment_start_date"].dropna()
        if not valid_dates.empty:
            min_enroll = valid_dates.min().date()
            max_enroll = valid_dates.max().date()
        else:
            min_enroll = _date.today()
            max_enroll = _date.today()
    else:
        min_enroll = _date.today()
        max_enroll = _date.today()
    date_range = st.date_input("Enrollment Date Range", value=[min_enroll, max_enroll])

# ── Apply filters ──────────────────────────────────────────────────────────────
df_filtered = df.copy()
if site_filter:
    df_filtered = df_filtered[df_filtered["site_name"].isin(site_filter)]
if status_filter:
    df_filtered = df_filtered[df_filtered["subject_status"].isin(status_filter)]
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
    if not df_filtered.empty and pd.api.types.is_datetime64_any_dtype(
        df_filtered["enrollment_start_date"]
    ):
        df_filtered = df_filtered[
            (df_filtered["enrollment_start_date"].dt.date >= start_date)
            & (df_filtered["enrollment_start_date"].dt.date <= end_date)
        ]

# ── KPI Row ────────────────────────────────────────────────────────────────────
total = len(df_filtered)
enrolled_count = (
    int((df_filtered["subject_status"] == "Enrolled").sum()) if not df_filtered.empty else 0
)
screened_count = (
    int((df_filtered["subject_status"] == "Screened").sum()) if not df_filtered.empty else 0
)
withdrawn_count = (
    int((df_filtered["subject_status"] == "Withdrawn").sum()) if not df_filtered.empty else 0
)
completed_count = (
    int((df_filtered["subject_status"] == "Completed").sum()) if not df_filtered.empty else 0
)

components.kpi_row(
    [
        {"label": "Total Subjects", "value": total},
        {"label": "Enrolled", "value": enrolled_count},
        {"label": "Screened", "value": screened_count},
        {"label": "Withdrawn", "value": withdrawn_count},
        {"label": "Completed", "value": completed_count},
    ]
)

# ── Two-column charts ──────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Subjects by Site")
    if not df_filtered.empty:
        site_counts = df_filtered.groupby("site_name").size().reset_index(name="count")
        render_accessible_chart(
            components.bar_chart(site_counts, x="count", y="site_name", title="Subjects per Site"),
            use_container_width=True,
        )

with col_right:
    st.subheader("Status Breakdown")
    if not df_filtered.empty:
        status_counts = df_filtered.groupby("subject_status").size().reset_index(name="count")
        render_accessible_chart(
            components.pie_chart(
                status_counts, theta="count", color="subject_status", title="Subject Status"
            ),
            use_container_width=True,
        )

# ── Cumulative enrollment trend ────────────────────────────────────────────────
st.subheader("Cumulative Enrollment Over Time")
df_enrolled = df_filtered[df_filtered["subject_status"] == "Enrolled"].copy()
if not df_enrolled.empty and pd.api.types.is_datetime64_any_dtype(
    df_enrolled["enrollment_start_date"]
):
    df_enrolled["enrollment_date"] = df_enrolled["enrollment_start_date"].dt.date
    df_trend = df_enrolled.groupby("enrollment_date").size().reset_index(name="count")
    df_trend = df_trend.sort_values("enrollment_date")
    df_trend["cumulative"] = df_trend["count"].cumsum()
    df_trend["enrollment_date"] = pd.to_datetime(df_trend["enrollment_date"])
    render_accessible_chart(
        components.line_chart(
            df_trend,
            x="enrollment_date",
            y="cumulative",
            title="Cumulative Enrolled Subjects",
        ),
        use_container_width=True,
    )

# ── Site enrollment rate table ─────────────────────────────────────────────────
st.subheader("Site Enrollment Summary")
if not df_filtered.empty:
    site_summary = (
        df_filtered.groupby("site_name")["subject_status"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ("Enrolled", "Screened", "Withdrawn"):
        if col not in site_summary.columns:
            site_summary[col] = 0
    site_summary = site_summary.rename(
        columns={
            "site_name": "Site",
            "Enrolled": "enrolled_count",
            "Screened": "screened_count",
            "Withdrawn": "withdrawn_count",
        }
    )
    site_totals = df_filtered.groupby("site_name").size().reset_index(name="total")
    site_summary = site_summary.merge(site_totals, left_on="Site", right_on="site_name", how="left")
    site_summary["enrollment_rate_pct"] = site_summary.apply(
        lambda row: (
            f"{row['enrolled_count'] / row['total'] * 100:.1f}%" if row["total"] > 0 else "N/A"
        ),
        axis=1,
    )
    display_cols = [
        "Site",
        "enrolled_count",
        "screened_count",
        "withdrawn_count",
        "enrollment_rate_pct",
    ]
    st.dataframe(
        site_summary[[c for c in display_cols if c in site_summary.columns]],
        use_container_width=True,
    )

# ── Subject data table and downloads ──────────────────────────────────────────
st.subheader("Subject List")
display_df = df_filtered.drop(columns=["deleted"], errors="ignore")
components.filterable_dataframe(display_df, key="enrollment_table")

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    components.csv_download_button(display_df, filename="subjects.csv")
with col_dl2:
    components.excel_download_button(display_df, filename="subjects.xlsx")
