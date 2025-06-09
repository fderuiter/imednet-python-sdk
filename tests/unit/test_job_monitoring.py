from unittest.mock import MagicMock

import pytest
from imednet.models.jobs import Job
from imednet.workflows import job_monitoring as jm
from imednet.workflows.job_monitoring import JobMonitoringWorkflow


def test_wait_for_job_success(monkeypatch):
    sdk = MagicMock()
    states = ["PENDING", "IN_PROGRESS", "COMPLETED"]

    def fake_get(study_key: str, batch_id: str) -> Job:
        return Job(jobId="1", batchId=batch_id, state=states.pop(0))

    sdk.jobs.get.side_effect = fake_get

    sleeps = []
    monkeypatch.setattr(jm.time, "sleep", lambda t: sleeps.append(t))

    workflow = JobMonitoringWorkflow(sdk)
    job = workflow.wait_for_job("S", "B", timeout=10, poll_interval=1)

    assert job.state == "COMPLETED"
    assert sleeps == [1, 1]


def test_wait_for_job_timeout(monkeypatch):
    sdk = MagicMock()
    sdk.jobs.get.return_value = Job(jobId="1", batchId="B", state="RUNNING")

    counter = {"i": 0}

    def fake_monotonic() -> int:
        counter["i"] += 1
        return counter["i"]

    monkeypatch.setattr(jm.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(jm.time, "sleep", lambda t: None)

    workflow = JobMonitoringWorkflow(sdk)
    with pytest.raises(TimeoutError):
        workflow.wait_for_job("S", "B", timeout=2, poll_interval=1)

    assert sdk.jobs.get.call_count >= 2


def test_wait_for_job_notify_and_interval(monkeypatch):
    sdk = MagicMock()
    states = ["PENDING", "COMPLETED"]

    def fake_get(study_key: str, batch_id: str) -> Job:
        return Job(jobId="1", batchId=batch_id, state=states.pop(0))

    sdk.jobs.get.side_effect = fake_get

    sleeps = []
    monkeypatch.setattr(jm.time, "sleep", lambda t: sleeps.append(t))

    notifications = []

    workflow = JobMonitoringWorkflow(sdk)
    job = workflow.wait_for_job(
        "S", "B", timeout=10, poll_interval=2, notify=lambda j: notifications.append(j.state)
    )

    assert job.state == "COMPLETED"
    assert notifications == ["PENDING", "COMPLETED"]
    assert sleeps == [2]
