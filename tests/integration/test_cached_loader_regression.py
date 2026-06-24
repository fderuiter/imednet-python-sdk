"""Regression tests for the CachedRecordsLoader.

These tests protect the durable behavior contracts for the cached loader,
ensuring that delta-sync, reconciliation, and iteration remain correct
across future refactors.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from imednet.spi.models import Record
from imednet_workflows.cached_loader import CachedRecordsLoader, get_cache_connection
from imednet_workflows.sync_worker import SyncWorker, SyncWorkerConfig


def _make_record(record_id: int, modified_at: str, study_key: str = "PROT-01") -> Record:
    """Helper to create a Record model for testing."""
    return Record(
        study_key=study_key,
        form_id=1,
        form_key="FORM",
        record_id=record_id,
        subject_key=f"S{record_id:04d}",
        date_modified=datetime.fromisoformat(modified_at.replace("Z", "+00:00")),
        record_data={"value": record_id},
    )


def test_delta_sync_progression_preserves_high_water_mark(tmp_path: Path) -> None:
    """Verify that incremental sync only fetches records modified since the last sync."""
    sdk = MagicMock()
    r1 = _make_record(1, "2024-01-01T10:00:00Z")
    r2 = _make_record(2, "2024-01-02T10:00:00Z")
    r3 = _make_record(3, "2024-01-03T10:00:00Z")

    # First sync: returns R1 and R2
    sdk.get_records.return_value = [r1, r2]
    loader = CachedRecordsLoader(sdk, cache_dir=tmp_path)
    loader.sync_records("PROT-01", reconcile=False)

    # Verify high water mark is R2's date
    with get_cache_connection(loader.db_path) as conn:
        hwm = loader._get_high_water_mark(conn, "PROT-01")
        # Ensure hwm is compared as a string (ISO format)
        expected_hwm = (
            r2.date_modified.isoformat()
            if hasattr(r2.date_modified, "isoformat")
            else str(r2.date_modified)
        )
        assert hwm == expected_hwm

    # Second sync: should request records since R2
    # Reset mock to track new calls
    sdk.get_records.reset_mock()
    sdk.records.list.reset_mock()
    sdk.records.list.return_value = [r3]

    loader.sync_records("PROT-01", reconcile=False)

    # Verify filter included dateModified >= R2's date
    # Note: CachedRecordsLoader uses build_filter_string which might produce different formats
    # but we care about the call to records.list
    sdk.records.list.assert_called_once()
    call_kwargs = sdk.records.list.call_args.kwargs
    assert "filter" in call_kwargs
    assert expected_hwm in call_kwargs["filter"]

    # Verify cache now has all three
    cached = loader.get_cached_records("PROT-01")
    assert {r.record_id for r in cached} == {1, 2, 3}


def test_reconciliation_removes_deleted_records(tmp_path: Path) -> None:
    """Verify that hard deletes in the upstream EDC are pruned from local cache."""
    sdk = MagicMock()
    r1 = _make_record(1, "2024-01-01T10:00:00Z")
    r2 = _make_record(2, "2024-01-02T10:00:00Z")

    # Initial sync: R1 and R2
    sdk.get_records.return_value = [r1, r2]
    loader = CachedRecordsLoader(sdk, cache_dir=tmp_path)
    loader.sync_records("PROT-01")

    assert len(loader.get_cached_records("PROT-01")) == 2

    # Second sync: R1 is deleted upstream.
    # sync_records calls get_records(deleted=False) to get active IDs.
    sdk.get_records.side_effect = [[r2], [r2]]  # First for delta (empty), second for reconcile
    sdk.records.list.return_value = []

    loader.sync_records("PROT-01", reconcile=True)

    # Verify R1 is gone
    cached = loader.get_cached_records("PROT-01")
    assert [r.record_id for r in cached] == [2]


def test_chunked_iteration_is_memory_efficient(tmp_path: Path) -> None:
    """Verify that iter_cached_records yields records in expected chunks."""
    sdk = MagicMock()
    records = [_make_record(i, f"2024-01-{i:02d}T10:00:00Z") for i in range(1, 11)]
    sdk.get_records.return_value = records

    loader = CachedRecordsLoader(sdk, cache_dir=tmp_path)
    loader.sync_records("PROT-01")

    # Iterate with chunk_size=3
    iterator = loader.iter_cached_records("PROT-01", chunk_size=3)

    # We can't easily verify internal SQLite "memory efficiency" without complex mocking,
    # but we can verify it yields all records and respects the interface.
    yielded = list(iterator)
    assert len(yielded) == 10
    assert [r.record_id for r in yielded] == list(range(1, 11))


def test_transient_failure_recovery(tmp_path: Path) -> None:
    """Verify that the loader retries on API failures and eventually succeeds."""
    sdk = MagicMock()
    r1 = _make_record(1, "2024-01-01T10:00:00Z")

    # Fail once then succeed
    sdk.get_records.side_effect = [RuntimeError("API Down"), [r1]]

    loader = CachedRecordsLoader(sdk, cache_dir=tmp_path, retry_attempts=2)

    # This should succeed due to retry
    loader.sync_records("PROT-01", reconcile=False)

    assert sdk.get_records.call_count == 2
    assert len(loader.get_cached_records("PROT-01")) == 1


def test_sync_worker_interaction_correctness(tmp_path: Path) -> None:
    """Verify that SyncWorker correctly triggers loader synchronization."""
    sdk = MagicMock()
    r1 = _make_record(1, "2024-01-01T10:00:00Z")
    sdk.get_records.return_value = [r1]

    loader = CachedRecordsLoader(sdk, cache_dir=tmp_path)
    worker = SyncWorker(
        loader, config=SyncWorkerConfig(study_key="PROT-01", interval_seconds=0, reconcile=True)
    )

    # run_once should call loader.sync_records (indirectly via load_records in some versions,
    # but current SyncWorker.run_once calls loader.load_records)
    worker.run_once()

    # Verify records were synced
    assert len(loader.get_cached_records("PROT-01")) == 1
