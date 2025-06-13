from unittest.mock import MagicMock

import pytest
from imednet.core.exceptions import JobTimeoutError
from imednet.models.jobs import JobStatus
from imednet.workflows.job_poller import JobPoller


def test_wait_success(monkeypatch) -> None:
    sdk = MagicMock()
    states = [
        JobStatus(batch_id="1", state="PROCESSING"),
        JobStatus(batch_id="1", state="COMPLETED"),
    ]
    monkeypatch.setattr(sdk.jobs, "get", lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *a: None)
    poller = JobPoller(sdk, "ST", "1", timeout_s=5, poll_interval_s=0)
    result = poller.wait()
    assert result.state == "COMPLETED"


def test_wait_timeout(monkeypatch) -> None:
    sdk = MagicMock()
    job = JobStatus(batch_id="1", state="PROCESSING")
    monkeypatch.setattr(sdk.jobs, "get", lambda s, b: job)
    counter = {"v": 0}

    def fake_monotonic() -> int:
        counter["v"] += 1
        return counter["v"]

    monkeypatch.setattr("time.monotonic", fake_monotonic)
    monkeypatch.setattr("time.sleep", lambda *a: None)
    poller = JobPoller(sdk, "ST", "1", timeout_s=2, poll_interval_s=0)
    with pytest.raises(JobTimeoutError):
        poller.wait()
