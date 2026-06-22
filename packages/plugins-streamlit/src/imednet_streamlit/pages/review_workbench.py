"""TODO: Add docstring."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from imednet.spi.models import TriageItem, TriageStatus
from imednet_streamlit.auth import get_study_key
from imednet_streamlit.components.triage_drawer import render_triage_drawer
from imednet_workflows.triage_store import TriageStore

_TRIAGE_DB_PATH_KEY = "_triage_db_path"
_SELECTED_ITEM_KEY = "_review_workbench_selected_item"
_DEFAULT_TRIAGE_DIR = Path.home() / ".imednet"
_STATUS_ORDER = {
    TriageStatus.NEW: 0,
    TriageStatus.UNDER_REVIEW: 1,
    TriageStatus.RESOLVED: 2,
}


def _get_store() -> TriageStore:
    """TODO: Add docstring."""
    raw_path = st.session_state.get(
        _TRIAGE_DB_PATH_KEY, str(_DEFAULT_TRIAGE_DIR / "triage.sqlite3")
    )
    db_path = _resolve_db_path(raw_path)
    return TriageStore(db_path)


def _resolve_db_path(raw_path: object) -> str:
    """TODO: Add docstring."""
    import os

    # Connect to managed database to support concurrent multi-user access
    if "IMEDNET_TRIAGE_DB_PATH" in os.environ:
        return os.environ["IMEDNET_TRIAGE_DB_PATH"]

    base_dir = _DEFAULT_TRIAGE_DIR.expanduser().resolve()
    candidate = Path(str(raw_path)).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    resolved = candidate.resolve()
    if not resolved.is_relative_to(base_dir):
        resolved = base_dir / "triage.sqlite3"
    return str(resolved)


def _last_activity(item: TriageItem) -> datetime | None:
    """TODO: Add docstring."""
    timestamps = [entry.timestamp for entry in item.history] + [
        annotation.timestamp for annotation in item.annotations
    ]
    return max(timestamps) if timestamps else None


def _age_hours(item: TriageItem) -> float:
    """TODO: Add docstring."""
    if item.status == TriageStatus.RESOLVED:
        return 0.0
    last_activity = _last_activity(item)
    if last_activity is None:
        return 0.0
    return (
        datetime.now(timezone.utc) - last_activity.astimezone(timezone.utc)
    ).total_seconds() / 3600.0


def _severity_bucket(severity: str) -> str:
    """TODO: Add docstring."""
    normalized = severity.strip().lower()
    if normalized in {"critical", "severe"}:
        return "Critical/Severe"
    if normalized in {"warning", "warn", "medium"}:
        return "Warning"
    return "Info"


def _category(item: TriageItem) -> str:
    """TODO: Add docstring."""
    prefix = item.item_id.split("-", 1)[0].upper()
    return {
        "AE": "Adverse Event",
        "PD": "Deviation",
        "DD": "Deficiency",
    }.get(prefix, "Other")


def _queue_dataframe(items: list[TriageItem]) -> pd.DataFrame:
    """TODO: Add docstring."""
    rows = [
        {
            "item_id": item.item_id,
            "severity": item.severity,
            "severity_bucket": _severity_bucket(item.severity),
            "category": _category(item),
            "status": item.status.value,
            "status_rank": _STATUS_ORDER[item.status],
            "assignee": item.assignee or "",
            "age_hours": round(_age_hours(item), 2),
        }
        for item in items
    ]
    if not rows:
        return pd.DataFrame(
            columns=[
                "item_id",
                "severity",
                "severity_bucket",
                "category",
                "status",
                "status_rank",
                "assignee",
                "age_hours",
            ]
        )
    return pd.DataFrame(rows)


def _render_kpis(queue_df: pd.DataFrame) -> None:
    """TODO: Add docstring."""
    open_count = int(queue_df[queue_df["status"] != TriageStatus.RESOLVED.value].shape[0])
    sla_warning_count = int(
        queue_df[
            (queue_df["status"] != TriageStatus.RESOLVED.value) & (queue_df["age_hours"] > 72.0)
        ].shape[0]
    )
    resolved_count = int(queue_df[queue_df["status"] == TriageStatus.RESOLVED.value].shape[0])

    col_open, col_sla, col_resolved = st.columns(3)
    with col_open:
        st.metric("Open Queue", open_count)
    with col_sla:
        st.metric("SLA >72h", sla_warning_count)
    with col_resolved:
        st.metric("Resolved", resolved_count)


def _filter_queue(queue_df: pd.DataFrame) -> pd.DataFrame:
    """TODO: Add docstring."""
    severity_options = sorted(queue_df["severity_bucket"].dropna().astype(str).unique().tolist())
    category_options = sorted(queue_df["category"].dropna().astype(str).unique().tolist())
    assignee_options = sorted(queue_df["assignee"].dropna().astype(str).unique().tolist())

    severity_filter = st.multiselect("Severity", severity_options, default=severity_options)
    category_filter = st.multiselect("Category", category_options, default=category_options)
    assignee_filter = st.multiselect("Assignee", assignee_options, default=assignee_options)
    search_term = st.text_input("Search by Subject Key")

    filtered = queue_df.copy()
    if severity_filter:
        filtered = filtered[filtered["severity_bucket"].isin(severity_filter)]
    if category_filter:
        filtered = filtered[filtered["category"].isin(category_filter)]
    if assignee_filter:
        filtered = filtered[filtered["assignee"].isin(assignee_filter)]
    if search_term:
        filtered = filtered[
            filtered["item_id"].astype(str).str.contains(search_term, case=False, na=False)
        ]

    return filtered.sort_values(["status_rank", "age_hours"], ascending=[True, False]).reset_index(
        drop=True
    )


def _get_current_user() -> str:
    """TODO: Add docstring."""
    user_value = st.session_state.get("_imednet_user", "reviewer")
    return str(user_value).strip() or "reviewer"


def render_page() -> None:
    """TODO: Add docstring."""
    st.title("🧪 Review Workbench")
    st.markdown(
        """
        <style>
        .triage-pill-critical {
            background-color:#FEE2E2;color:#B91C1C;border-radius:999px;padding:2px 10px;
        }
        .triage-pill-warning {
            background-color:#FEF3C7;color:#92400E;border-radius:999px;padding:2px 10px;
        }
        .triage-pill-info {
            background-color:#DBEAFE;color:#1E3A8A;border-radius:999px;padding:2px 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    study_key = get_study_key()
    store = _get_store()
    items = store.get_queue(study_key)

    if not items:
        st.info("No triage items available.")
        return

    queue_df = _queue_dataframe(items)
    _render_kpis(queue_df)

    filtered_df = _filter_queue(queue_df)
    if filtered_df.empty:
        st.info("No triage items match the selected filters.")
        return

    display_df = filtered_df[["item_id", "severity", "category", "status", "assignee", "age_hours"]]
    st.dataframe(display_df, use_container_width=True)

    item_options = filtered_df["item_id"].tolist()
    selected_item_id = st.session_state.get(_SELECTED_ITEM_KEY, item_options[0])
    selected_item_id = st.selectbox(
        "Select item",
        item_options,
        index=item_options.index(selected_item_id) if selected_item_id in item_options else 0,
    )
    st.session_state[_SELECTED_ITEM_KEY] = selected_item_id

    selected_item = next((item for item in items if item.item_id == selected_item_id), None)
    if selected_item is None:
        return

    assignee_options = sorted({(item.assignee or "Unassigned") for item in items})
    if "Unassigned" not in assignee_options:
        assignee_options.insert(0, "Unassigned")
    current_user = _get_current_user()
    if current_user not in assignee_options:
        assignee_options.append(current_user)

    render_triage_drawer(
        store=store,
        item=selected_item,
        assignee_options=assignee_options,
        current_user=current_user,
    )


render_page()
