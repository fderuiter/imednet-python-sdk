from unittest.mock import MagicMock

import pytest
from imednet.models.jobs import Job
from imednet.utils.jobs import wait_for_job


def test_wait_for_job_stops_on_terminal(monkeypatch) -> None:
    sdk = MagicMock()
    sdk.jobs.get.side_effect = [
        Job(batch_id="1", state="PROCESSING"),
        Job(batch_id="1", state="COMPLETED"),
    ]
    monkeypatch.setattr("time.sleep", lambda *args: None)
    job = wait_for_job(sdk, "STUDY", "1", timeout=5, poll_interval=0)
    assert job.state == "COMPLETED"
    assert sdk.jobs.get.call_count == 2
    for call in sdk.jobs.get.call_args_list:
        assert call.args == ("STUDY", "1")


def test_wait_for_job_times_out(monkeypatch) -> None:
    sdk = MagicMock()
    sdk.jobs.get.return_value = Job(batch_id="1", state="PROCESSING")

    counter = {"t": 0}

    def fake_monotonic() -> int:
        counter["t"] += 1
        return counter["t"]

    monkeypatch.setattr("time.monotonic", fake_monotonic)
    monkeypatch.setattr("time.sleep", lambda *args: None)

    with pytest.raises(TimeoutError):
        wait_for_job(sdk, "STUDY", "1", timeout=2, poll_interval=0)
    assert sdk.jobs.get.call_count >= 1
