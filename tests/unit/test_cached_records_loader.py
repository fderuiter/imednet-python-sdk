from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from unittest.mock import MagicMock

from imednet.models.records import Record
from imednet_workflows.cached_loader import CachedRecordsLoader, get_cache_connection


def _record(record_id: int, date_modified: datetime) -> Record:
    return Record(
        study_key="STUDY",
        record_id=record_id,
        date_modified=date_modified,
        subject_key=f"S{record_id}",
        visit_id=record_id,
    )


def test_get_cache_connection_enables_wal(tmp_path) -> None:
    db_path = tmp_path / "cache.db"

    with get_cache_connection(str(db_path)) as conn:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]

    assert mode.lower() == "wal"


def test_loader_initializes_database_in_configurable_directory(tmp_path) -> None:
    sdk = MagicMock()
    loader = CachedRecordsLoader(sdk, cache_dir=str(tmp_path), db_name="records_cache_test.db")

    assert loader.db_path == str(tmp_path / "records_cache_test.db")
    assert (tmp_path / "records_cache_test.db").exists()

    with sqlite3.connect(loader.db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }

    assert {"record_cache", "cache_metadata"}.issubset(tables)


def test_sync_runs_delta_upsert_and_hard_delete_reconciliation(tmp_path) -> None:
    sdk = MagicMock()
    first_delta = [
        _record(1, datetime(2026, 1, 1, tzinfo=timezone.utc)),
        _record(2, datetime(2026, 1, 2, tzinfo=timezone.utc)),
    ]
    first_active = [_record(1, datetime(2026, 1, 2, tzinfo=timezone.utc))]
    second_delta = [_record(3, datetime(2026, 1, 3, tzinfo=timezone.utc))]
    second_active = [
        _record(1, datetime(2026, 1, 2, tzinfo=timezone.utc)),
        _record(3, datetime(2026, 1, 3, tzinfo=timezone.utc)),
    ]
    sdk.records.list.side_effect = [first_delta, first_active, second_delta, second_active]

    loader = CachedRecordsLoader(sdk, cache_dir=str(tmp_path), reconcile_interval_seconds=9999)
    first_result = loader.load_records("STUDY", force_reconcile=True)
    second_result = loader.load_records("STUDY", force_reconcile=True)

    assert [record.record_id for record in first_result] == [1]
    assert [record.record_id for record in second_result] == [1, 3]

    second_delta_call = sdk.records.list.call_args_list[2]
    assert second_delta_call.kwargs["study_key"] == "STUDY"
    assert second_delta_call.kwargs["date_modified"][0] == ">"
    assert second_delta_call.kwargs["date_modified"][1].startswith("2026-01-02")

    first_reconcile_call = sdk.records.list.call_args_list[1]
    assert first_reconcile_call.kwargs["deleted"] is False


def test_delta_fetch_retries_on_transient_failure(tmp_path) -> None:
    sdk = MagicMock()
    record = _record(7, datetime(2026, 1, 5, tzinfo=timezone.utc))
    sdk.records.list.side_effect = [RuntimeError("temporary API error"), [record]]

    loader = CachedRecordsLoader(sdk, cache_dir=str(tmp_path), reconcile_interval_seconds=9999)
    loader._set_last_reconciled("STUDY", datetime.now(timezone.utc))
    result = loader.load_records("STUDY")

    assert [item.record_id for item in result] == [7]
    assert sdk.records.list.call_count == 2
