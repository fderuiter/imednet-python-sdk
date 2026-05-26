from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from imednet.models.triage import TriageAnnotation, TriageHistoryEntry, TriageItem, TriageStatus
from imednet_workflows.triage_store import TriageStore


def _seed_item(item_id: str = "AE-1") -> TriageItem:
    return TriageItem(
        item_id=item_id,
        study_key="STUDY-A",
        status=TriageStatus.NEW,
        assignee="triager",
        severity="critical",
        annotations=[
            TriageAnnotation(
                annotation_id=f"note-{item_id}",
                user_id="triager",
                comment="initial note",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=96),
            )
        ],
        history=[
            TriageHistoryEntry(
                transition_id=f"hist-{item_id}",
                from_status=TriageStatus.NEW,
                to_status=TriageStatus.NEW,
                user_id="triager",
                comment="created",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=95),
            )
        ],
    )


def test_triage_store_enables_wal_mode(tmp_path: Path) -> None:
    store = TriageStore(tmp_path / "triage.sqlite3")
    assert store.get_journal_mode().lower() == "wal"


def test_triage_store_crud_and_queue_filters(tmp_path: Path) -> None:
    store = TriageStore(tmp_path / "triage.sqlite3")
    store.upsert_item(_seed_item("AE-1"))
    store.upsert_item(_seed_item("PD-2"))

    store.assign_item("AE-1", "lead-reviewer")
    store.add_annotation("AE-1", "lead-reviewer", "  investigate severity  ")
    store.update_status("AE-1", TriageStatus.UNDER_REVIEW, "lead-reviewer", "started")

    item = store.get_triage_item("AE-1")
    assert item is not None
    assert item.assignee == "lead-reviewer"
    assert item.status == TriageStatus.UNDER_REVIEW
    assert item.annotations[-1].comment == "investigate severity"
    assert item.history[-1].to_status == TriageStatus.UNDER_REVIEW

    full_queue = store.get_queue("STUDY-A")
    under_review_queue = store.get_queue("STUDY-A", status=TriageStatus.UNDER_REVIEW)

    assert {queued_item.item_id for queued_item in full_queue} == {"AE-1", "PD-2"}
    assert [queued_item.item_id for queued_item in under_review_queue] == ["AE-1"]


def test_triage_store_handles_parallel_reads_and_writes(tmp_path: Path) -> None:
    store = TriageStore(tmp_path / "triage.sqlite3")
    store.upsert_item(_seed_item("AE-99"))

    def _writer(idx: int) -> None:
        store.add_annotation("AE-99", f"user-{idx}", f"comment {idx}")

    def _reader() -> int:
        item = store.get_triage_item("AE-99")
        assert item is not None
        return len(item.annotations)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_writer, idx) for idx in range(10)] + [
            pool.submit(_reader) for _ in range(10)
        ]

    failures = [future.exception() for future in futures if future.exception() is not None]
    assert failures == []

    latest = store.get_triage_item("AE-99")
    assert latest is not None
    assert len(latest.annotations) >= 11


def test_triage_store_rejects_empty_annotation_comment(tmp_path: Path) -> None:
    store = TriageStore(tmp_path / "triage.sqlite3")
    store.upsert_item(_seed_item("DD-4"))

    with pytest.raises(ValueError, match="must not be empty"):
        store.add_annotation("DD-4", "triager", "   ")
