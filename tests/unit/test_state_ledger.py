"""Unit tests for state ledger."""

from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone

import pytest

import imednet_workflows.state_ledger as _state_ledger_module
from imednet_workflows.state_ledger import ExtractionStateLedger, LedgerState


def test_state_ledger_read_write(tmp_path) -> None:
    """Test that state ledger read write."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))

    # Initial state should be empty
    state = ledger.read_state()
    assert isinstance(state, LedgerState)
    assert len(state.studies) == 0

    # Write state
    ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    ledger.set_last_timestamp(
        study_key="STUDY-01",
        stream_name="records",
        timestamp=ts,
        records_processed=42,
        status="success",
        metadata={"foo": "bar"},
    )

    # Read state back
    state2 = ledger.read_state()
    assert "STUDY-01" in state2.studies
    stream = state2.studies["STUDY-01"].streams["records"]
    assert stream.last_timestamp == ts
    assert stream.records_processed == 42
    assert stream.last_run_status == "success"
    assert stream.metadata == {"foo": "bar"}

    # Get last timestamp convenience method
    retrieved_ts = ledger.get_last_timestamp("STUDY-01", "records")
    assert retrieved_ts == ts

    # Missing study/stream should return None
    assert ledger.get_last_timestamp("STUDY-02", "records") is None
    assert ledger.get_last_timestamp("STUDY-01", "queries") is None


def test_state_ledger_transaction_success(tmp_path) -> None:
    """Test that state ledger transaction success."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))
    fallback_ts = datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc)

    # Successful transaction
    new_ts = datetime(2026, 5, 22, 11, 0, 0, tzinfo=timezone.utc)
    with ledger.transaction("STUDY-01", "records", fallback_timestamp=fallback_ts) as tx:
        assert tx["last_timestamp"] == fallback_ts
        tx["new_timestamp"] = new_ts
        tx["records_processed"] = 100
        tx["metadata"] = {"batch": 1}

    # Verify state was committed
    retrieved_ts = ledger.get_last_timestamp("STUDY-01", "records")
    assert retrieved_ts == new_ts

    state = ledger.read_state()
    stream = state.studies["STUDY-01"].streams["records"]
    assert stream.records_processed == 100
    assert stream.last_run_status == "success"
    assert stream.metadata == {"batch": 1}


def test_state_ledger_transaction_failure(tmp_path) -> None:
    """Test that state ledger transaction failure."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))
    fallback_ts = datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc)

    # Failed transaction due to an raised exception
    with pytest.raises(ValueError, match="API Error"):
        with ledger.transaction("STUDY-01", "records", fallback_timestamp=fallback_ts) as tx:
            assert tx["last_timestamp"] == fallback_ts
            tx["records_processed"] = 10
            raise ValueError("API Error")

    # Verify state is updated to failed and error message registered
    state = ledger.read_state()
    stream = state.studies["STUDY-01"].streams["records"]
    assert stream.last_run_status == "failed"
    assert stream.error_message == "API Error"
    assert stream.records_processed == 10


def test_state_ledger_atomic_write_failure(tmp_path, monkeypatch) -> None:
    """Test that state ledger atomic write failure."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))

    # Pre-populate state
    ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    ledger.set_last_timestamp("STUDY-01", "records", ts)

    # Mock os.replace to raise an error
    def mock_replace(src, dst):
        """Helper function to mock replace."""
        raise OSError("Disk full")

    monkeypatch.setattr(os, "replace", mock_replace)

    # Attempt to write new state should raise OSError
    new_ts = datetime(2026, 5, 22, 13, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(OSError, match="Disk full"):
        ledger.set_last_timestamp("STUDY-01", "records", new_ts)

    # Verify original state was preserved
    monkeypatch.undo()
    assert ledger.get_last_timestamp("STUDY-01", "records") == ts


@pytest.mark.skipif(
    _state_ledger_module.fcntl is None,
    reason="flock not available on this platform (no fcntl)",
)
def test_state_ledger_flock_concurrency(tmp_path) -> None:
    """Test that state ledger flock concurrency."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))

    # Fill state
    ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    ledger.set_last_timestamp("STUDY-01", "records", ts)

    lock_acquired = threading.Event()
    release_lock = threading.Event()
    thread_done = threading.Event()

    def locking_thread():
        """Helper function to locking thread."""
        with ledger._lock():
            lock_acquired.set()
            release_lock.wait()
        thread_done.set()

    # Start a thread to acquire lock and hold it
    t = threading.Thread(target=locking_thread)
    t.start()

    # Wait for the thread to acquire the lock
    lock_acquired.wait(timeout=2.0)
    assert lock_acquired.is_set()

    # Try to acquire lock in main thread, it should block/wait.
    # Since we can't easily wait with timeout on flock directly in blocking way,
    # we verify that a second thread trying to acquire lock takes time.
    time.time()
    lock_acquired_in_t2 = threading.Event()

    def second_thread():
        """Helper function to second thread."""
        with ledger._lock():
            lock_acquired_in_t2.set()

    t2 = threading.Thread(target=second_thread)
    t2.start()

    # Main thread sleeps a bit, then releases the lock from the first thread
    time.sleep(0.5)
    assert not lock_acquired_in_t2.is_set()

    release_lock.set()
    lock_acquired_in_t2.wait(timeout=2.0)
    assert lock_acquired_in_t2.is_set()

    # Cleanup threads
    t.join()
    t2.join()


def test_delete_entry_removes_whole_study(tmp_path) -> None:
    """Test that delete entry removes whole study."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))
    ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    ledger.set_last_timestamp("STUDY-01", "records", ts)
    ledger.set_last_timestamp("STUDY-02", "records", ts)

    removed = ledger.delete_entry("STUDY-01")

    assert removed is True
    state = ledger.read_state()
    assert "STUDY-01" not in state.studies
    assert "STUDY-02" in state.studies


def test_delete_entry_removes_specific_stream(tmp_path) -> None:
    """Test that delete entry removes specific stream."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))
    ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    ledger.set_last_timestamp("STUDY-01", "records", ts)
    ledger.set_last_timestamp("STUDY-01", "queries", ts)

    removed = ledger.delete_entry("STUDY-01", stream_name="records")

    assert removed is True
    state = ledger.read_state()
    assert "STUDY-01" in state.studies
    assert "records" not in state.studies["STUDY-01"].streams
    assert "queries" in state.studies["STUDY-01"].streams


def test_delete_entry_returns_false_when_study_not_found(tmp_path) -> None:
    """Test that delete entry returns false when study not found."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))

    removed = ledger.delete_entry("NONEXISTENT-STUDY")

    assert removed is False


def test_delete_entry_returns_false_when_stream_not_found(tmp_path) -> None:
    """Test that delete entry returns false when stream not found."""
    ledger_file = tmp_path / "ledger.json"
    ledger = ExtractionStateLedger(str(ledger_file))
    ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    ledger.set_last_timestamp("STUDY-01", "records", ts)

    removed = ledger.delete_entry("STUDY-01", stream_name="nonexistent-stream")

    assert removed is False
    state = ledger.read_state()
    assert "records" in state.studies["STUDY-01"].streams


def test_corrupted_ledger_recovery(tmp_path) -> None:
    """Test that corrupted ledger recovery."""
    ledger_file = tmp_path / "ledger.json"
    # Write garbage content to file
    with open(ledger_file, "w") as f:
        f.write("corrupted JSON data {")

    ledger = ExtractionStateLedger(str(ledger_file))
    state = ledger.read_state()
    # Should recover gracefully with empty state
    assert len(state.studies) == 0


def test_get_state_provider_airflow(monkeypatch):
    """Test get_state_provider returns AirflowStateProvider when USE_AIRFLOW_STATE_PROVIDER=1."""
    monkeypatch.setenv("USE_AIRFLOW_STATE_PROVIDER", "1")
    from imednet_workflows.state_ledger import AirflowStateProvider, get_state_provider

    provider = get_state_provider()
    assert isinstance(provider, AirflowStateProvider)


def test_airflow_state_provider_methods():
    import sys
    from unittest.mock import patch

    with patch.dict(
        sys.modules,
        {
            'airflow': None,
            'airflow.models.xcom': None,
            'airflow.utils.session': None,
            'airflow.operators.python': None,
        },
    ):
        from imednet_workflows.state_ledger import AirflowStateProvider

        provider = AirflowStateProvider()
        assert provider.get_last_timestamp("STUDY-01", "records") is None
        ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
        provider.set_last_timestamp("STUDY-01", "records", ts)
        assert provider.delete_entry("STUDY-01") is False
        state = provider.read_state()
        assert len(state.studies) == 0


def test_airflow_state_provider_transaction_success():
    import sys
    from unittest.mock import patch

    with patch.dict(
        sys.modules,
        {
            'airflow': None,
            'airflow.models.xcom': None,
            'airflow.utils.session': None,
            'airflow.operators.python': None,
        },
    ):
        from imednet_workflows.state_ledger import AirflowStateProvider

        provider = AirflowStateProvider()
        fallback_ts = datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc)
        with provider.transaction("STUDY-01", "records", fallback_timestamp=fallback_ts) as tx:
            tx["new_timestamp"] = datetime(2026, 5, 22, 11, 0, 0, tzinfo=timezone.utc)


def test_airflow_state_provider_transaction_error():
    import sys
    from unittest.mock import patch

    with patch.dict(
        sys.modules,
        {
            'airflow': None,
            'airflow.models.xcom': None,
            'airflow.utils.session': None,
            'airflow.operators.python': None,
        },
    ):
        from imednet_workflows.state_ledger import AirflowStateProvider

        provider = AirflowStateProvider()
        fallback_ts = datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError):
            with provider.transaction("STUDY-01", "records", fallback_timestamp=fallback_ts):
                raise ValueError("Test error")
