from unittest.mock import MagicMock

import pytest
from imednet.models.jobs import Job
from imednet.workflows.job_poller import JobPoller, JobTimeoutError


def test_wait_success(monkeypatch) -> None:
    sdk = MagicMock()
    states = [Job(batch_id="1", state="PROCESSING"), Job(batch_id="1", state="COMPLETED")]
    sdk.jobs.get.side_effect = lambda s, b: states.pop(0)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(sdk, "ST", "1", timeout_s=5, poll_interval_s=0)
    result = poller.wait()
    assert result.state == "COMPLETED"


def test_wait_timeout(monkeypatch) -> None:
    sdk = MagicMock()
    sdk.jobs.get.return_value = Job(batch_id="1", state="PROCESSING")
    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(sdk, "ST", "1", timeout_s=1, poll_interval_s=0)
    with pytest.raises(JobTimeoutError):
        poller.wait()
