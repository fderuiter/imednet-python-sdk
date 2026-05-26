from __future__ import annotations

from typing import Sequence

import streamlit as st

from imednet.models.triage import TriageItem, TriageStatus
from imednet_workflows.triage_store import TriageStore


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

    timeline: list[tuple[str, str]] = []
    for entry in item.history:
        detail = f"{entry.from_status.value} → {entry.to_status.value} by {entry.user_id}"
        if entry.comment:
            detail += f" — {entry.comment}"
        timeline.append((entry.timestamp.isoformat(), detail))
    for annotation in item.annotations:
        timeline.append(
            (
                annotation.timestamp.isoformat(),
                f"Annotation by {annotation.user_id}: {annotation.comment}",
            )
        )

    for _, message in sorted(timeline, key=lambda record: record[0]):
        st.write(f"• {message}")

    current_assignee = item.assignee if item.assignee in assignee_options else None
    assign_selection = st.selectbox(
        "Change Assignee",
        options=list(assignee_options),
        index=(list(assignee_options).index(current_assignee) if current_assignee else 0),
        key=f"assignee_{item.item_id}",
    )
    if st.button("Assign", key=f"assign_btn_{item.item_id}"):
        store.assign_item(item.item_id, assign_selection)
        st.success("Assignee updated")

    annotation_text = st.text_area("Annotate", key=f"annotation_{item.item_id}")
    if st.button("Save Annotation", key=f"annotation_btn_{item.item_id}"):
        if annotation_text.strip():
            store.add_annotation(item.item_id, current_user, annotation_text)
            st.success("Annotation added")
        else:
            st.warning("Annotation comment is required.")

    status_value = st.selectbox(
        "Triage Capture",
        options=[status.value for status in TriageStatus],
        index=[status.value for status in TriageStatus].index(item.status.value),
        key=f"status_{item.item_id}",
    )
    if st.button("Update Status", key=f"status_btn_{item.item_id}"):
        store.update_status(
            item.item_id,
            TriageStatus(status_value),
            current_user,
            annotation_text or None,
        )
        st.success("Status updated")
