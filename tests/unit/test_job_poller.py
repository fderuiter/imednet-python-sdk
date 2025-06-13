from types import SimpleNamespace

import pytest
from imednet.core.exceptions import JobTimeoutError
from imednet.models.jobs import Job
from imednet.workflows.job_poller import JobPoller


def make_sdk(mock_get):
    return SimpleNamespace(jobs=SimpleNamespace(get=mock_get))


def test_wait_success(monkeypatch):
    states = ["IN_PROGRESS", "IN_PROGRESS", "COMPLETED"]

    def fake_get(study_key, job_id):
        return Job(job_id="j1", batch_id=job_id, state=states.pop(0))

    sdk = make_sdk(fake_get)
    poller = JobPoller(sdk, "study", "b1", timeout_s=2, poll_interval_s=0)
    monkeypatch.setattr("time.sleep", lambda s: None)
    result = poller.wait()
    assert result.state == "COMPLETED"


def test_wait_timeout(monkeypatch):
    def fake_get(study_key, job_id):
        return Job(job_id="j1", batch_id=job_id, state="IN_PROGRESS")

    sdk = make_sdk(fake_get)
    poller = JobPoller(sdk, "study", "b1", timeout_s=0.01, poll_interval_s=0)

    times = [0.0]

    def fake_monotonic():
        times[0] += 0.005
        return times[0]

    monkeypatch.setattr("time.sleep", lambda s: None)
    monkeypatch.setattr("time.monotonic", fake_monotonic)
    with pytest.raises(JobTimeoutError):
        poller.wait()
