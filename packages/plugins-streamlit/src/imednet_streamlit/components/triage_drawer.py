from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

import streamlit as st

from imednet.models.triage import TriageItem, TriageStatus
from imednet_workflows.triage_store import TriageStore

_LAST_ACTION_KEY = "_triage_drawer_last_action"
_TIMELINE_COL_RATIO = 3
_ACTION_COL_RATIO = 2
_DECISION_BUTTON_COLS = [1, 1, 1]


def _record_action(
    *,
    item_id: str,
    action: str,
    status: TriageStatus | None = None,
    assignee: str | None = None,
    comment: str | None = None,
) -> None:
    st.session_state[_LAST_ACTION_KEY] = {
        "item_id": item_id,
        "action": action,
        "status": status.value if status else None,
        "assignee": assignee,
        "comment": comment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def render_triage_drawer(
    *,
    store: TriageStore,
    item: TriageItem,
    assignee_options: Sequence[str],
    current_user: str,
) -> None:
    """Render triage detail and actions for a selected item."""

    st.subheader(f"Review Item: {item.item_id}")
    st.caption(f"Study: {item.study_key} • Severity: {item.severity} • Status: {item.status.value}")

    timeline_entries: list[tuple[datetime, str]] = []
    for entry in item.history:
        detail = f"{entry.from_status.value} → {entry.to_status.value} by {entry.user_id}"
        if entry.comment:
            detail += f" — {entry.comment}"
        timeline_entries.append((entry.timestamp, detail))
    for annotation in item.annotations:
        timeline_entries.append(
            (
                annotation.timestamp,
                f"Annotation by {annotation.user_id}: {annotation.comment}",
            )
        )

    timeline_col, action_col = st.columns([_TIMELINE_COL_RATIO, _ACTION_COL_RATIO], gap="large")
    with timeline_col:
        st.markdown("### Timeline")
        for timestamp, message in sorted(timeline_entries, key=lambda record: record[0]):
            st.write(f"• {timestamp.strftime('%Y-%m-%d %H:%M UTC')} — {message}")

    with action_col:
        st.markdown("### Actions")
        current_assignee = item.assignee if item.assignee in assignee_options else None
        assign_selection = st.selectbox(
            "Change Assignee",
            options=list(assignee_options),
            index=(list(assignee_options).index(current_assignee) if current_assignee else 0),
            key=f"assignee_{item.item_id}",
        )
        if st.button("Assign", key=f"assign_btn_{item.item_id}"):
            store.assign_item(item.item_id, assign_selection)
            _record_action(item_id=item.item_id, action="assign", assignee=assign_selection)
            st.success("Assignee updated")

        annotation_text = st.text_area("Annotate", key=f"annotation_{item.item_id}")
        if st.button("Save Annotation", key=f"annotation_btn_{item.item_id}"):
            cleaned_annotation = annotation_text.strip()
            if cleaned_annotation:
                store.add_annotation(item.item_id, current_user, cleaned_annotation)
                _record_action(item_id=item.item_id, action="annotate", comment=cleaned_annotation)
                st.success("Annotation added")
            else:
                st.warning("Annotation comment is required.")

        st.markdown("#### Triage Capture")
        triage_col, reject_col, approve_col = st.columns(_DECISION_BUTTON_COLS)

        if triage_col.button("Triage", key=f"triage_btn_{item.item_id}"):
            cleaned_annotation = annotation_text.strip()
            store.update_status(
                item.item_id,
                TriageStatus.UNDER_REVIEW,
                current_user,
                cleaned_annotation or None,
            )
            _record_action(
                item_id=item.item_id,
                action="triage",
                status=TriageStatus.UNDER_REVIEW,
                comment=cleaned_annotation or None,
            )
            st.success("Item triaged")

        if reject_col.button("Reject", key=f"reject_btn_{item.item_id}"):
            cleaned_annotation = annotation_text.strip()
            decision_comment = (
                f"Rejected: {cleaned_annotation}" if cleaned_annotation else "Rejected"
            )
            store.update_status(item.item_id, TriageStatus.RESOLVED, current_user, decision_comment)
            _record_action(
                item_id=item.item_id,
                action="reject",
                status=TriageStatus.RESOLVED,
                comment=decision_comment,
            )
            st.success("Item rejected")

        if approve_col.button("Approve", key=f"approve_btn_{item.item_id}"):
            cleaned_annotation = annotation_text.strip()
            decision_comment = (
                f"Approved: {cleaned_annotation}" if cleaned_annotation else "Approved"
            )
            store.update_status(item.item_id, TriageStatus.RESOLVED, current_user, decision_comment)
            _record_action(
                item_id=item.item_id,
                action="approve",
                status=TriageStatus.RESOLVED,
                comment=decision_comment,
            )
            st.success("Item approved")
