"""Test Sync Worker module."""

from __future__ import annotations

from threading import Event
from unittest.mock import MagicMock

from imednet_workflows.sync_worker import SyncWorker, SyncWorkerConfig


def test_sync_worker_run_once_syncs_with_lock(tmp_path) -> None:
    """Test the test sync worker run once syncs with lock functionality."""
    loader = MagicMock()
    loader.db_path = tmp_path / "records_cache.sqlite3"
    loader.load_records.return_value = [MagicMock(), MagicMock()]

    worker = SyncWorker(loader, config=SyncWorkerConfig(study_key="PROT-01", interval_seconds=1))

    synced_count = worker.run_once()

    assert synced_count == 2
    loader.load_records.assert_called_once_with("PROT-01", reconcile=True)


def test_sync_worker_run_forever_stops_gracefully(tmp_path) -> None:
    """Test the test sync worker run forever stops gracefully functionality."""
    loader = MagicMock()
    loader.db_path = tmp_path / "records_cache.sqlite3"
    stop_event = Event()
    worker = SyncWorker(
        loader,
        config=SyncWorkerConfig(study_key="PROT-01", interval_seconds=60),
        stop_event=stop_event,
    )

    def _stop_after_first_cycle(*args, **kwargs) -> list[MagicMock]:
        """Test the stop after first cycle functionality."""
        stop_event.set()
        return []

    loader.load_records.side_effect = _stop_after_first_cycle
    worker.run_forever()

    loader.load_records.assert_called_once_with("PROT-01", reconcile=True)
