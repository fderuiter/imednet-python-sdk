"""TODO: Add docstring."""
from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_DRAWER_BUTTON_COUNT = 5
_SAVE_ANNOTATION_BUTTON_INDEX = 1
_APPROVE_BUTTON_INDEX = 4


def _triage_drawer_app() -> None:
    """TODO: Add docstring."""
    import tempfile
    import uuid
    from datetime import datetime, timezone
    from pathlib import Path

    import streamlit as st

    from imednet.models.triage import TriageHistoryEntry, TriageItem, TriageStatus
    from imednet_streamlit.components.triage_drawer import render_triage_drawer
    from imednet_workflows.triage_store import TriageStore

    db_path = st.session_state.get("_triage_drawer_test_db_path")
    if not isinstance(db_path, str):
        db_path = str(Path(tempfile.gettempdir()) / f"triage-drawer-{uuid.uuid4().hex}.sqlite3")
        st.session_state["_triage_drawer_test_db_path"] = db_path

    store = TriageStore(db_path)
    if not st.session_state.get("_seeded_item"):
        store.upsert_item(
            TriageItem(
                item_id="AE-1",
                study_key="STUDY-X",
                status=TriageStatus.NEW,
                assignee="alice",
                severity="critical",
                history=[
                    TriageHistoryEntry(
                        transition_id="h-1",
                        from_status=TriageStatus.NEW,
                        to_status=TriageStatus.NEW,
                        user_id="reviewer",
                        comment="created",
                        timestamp=datetime.now(timezone.utc),
                    )
                ],
                annotations=[],
            )
        )
        st.session_state["_seeded_item"] = True

    item = store.get_queue("STUDY-X")[0]
    render_triage_drawer(
        store=store,
        item=item,
        assignee_options=["alice", "reviewer"],
        current_user="reviewer",
    )


def test_triage_drawer_submission_updates_session_state_and_persistence() -> None:
    """TODO: Add docstring."""
    from imednet.models.triage import TriageStatus
    from imednet_workflows.triage_store import TriageStore

    at = AppTest.from_function(_triage_drawer_app)
    try:
        at.run()
        assert len(at.exception) == 0
        assert len(at.text_area) == 1
        assert len(at.button) == _DRAWER_BUTTON_COUNT

        at.text_area[0].input("needs follow-up")
        at.button[_SAVE_ANNOTATION_BUTTON_INDEX].click()
        at.run()

        assert at.session_state["_triage_drawer_last_action"]["action"] == "annotate"
        assert at.session_state["_triage_drawer_last_action"]["comment"] == "needs follow-up"

        at.text_area[0].input("ready for approval")
        at.button[_APPROVE_BUTTON_INDEX].click()
        at.run()

        assert at.session_state["_triage_drawer_last_action"]["action"] == "approve"
        assert (
            at.session_state["_triage_drawer_last_action"]["status"] == TriageStatus.RESOLVED.value
        )

        db_path = str(at.session_state["_triage_drawer_test_db_path"])
        store = TriageStore(db_path)
        item = store.get_queue("STUDY-X")[0]
        assert item.status == TriageStatus.RESOLVED
        assert [annotation.comment for annotation in item.annotations] == ["needs follow-up"]
        assert item.history[-1].to_status == TriageStatus.RESOLVED
        assert item.history[-1].comment == "Approved: ready for approval"
    finally:
        if "_triage_drawer_test_db_path" in at.session_state:
            db_path = at.session_state["_triage_drawer_test_db_path"]
            if isinstance(db_path, str):
                Path(db_path).unlink(missing_ok=True)
