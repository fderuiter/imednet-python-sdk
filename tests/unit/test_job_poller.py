from unittest.mock import MagicMock

import pytest
from imednet.models.jobs import Job
from imednet.workflows.job_poller import JobPoller, JobTimeoutError


def test_wait_success(monkeypatch) -> None:
    get_job = MagicMock()
    states = [Job(batch_id="1", state="PROCESSING"), Job(batch_id="1", state="COMPLETED")]
    get_job.side_effect = lambda s, b: states.pop(0)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job, False)
    result = poller.run("ST", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


def test_wait_timeout(monkeypatch) -> None:
    get_job = MagicMock(return_value=Job(batch_id="1", state="PROCESSING"))
    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job, False)
    with pytest.raises(JobTimeoutError):
        poller.run("ST", "1", interval=0, timeout=1)
