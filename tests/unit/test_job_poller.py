"""Tests for JobPoller and AsyncJobPoller."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.models.jobs import JobStatus
from imednet.utils.job_poller import (
    AsyncJobPoller,
    JobPoller,
    JobStatusEvent,
    JobTimeoutError,
    JobFailedError,
)


def test_job_poller_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful synchronous job polling."""
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)
    result = poller.run("ST", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


@pytest.mark.asyncio
async def test_async_job_poller_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful asynchronous job polling."""
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl=""),
    ]
    get_job = AsyncMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = AsyncJobPoller(get_job)
    result = await poller.run("ST", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


def test_job_poller_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test synchronous job polling timeout."""
    job = JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl="")
    get_job = MagicMock(return_value=job)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)

    tick = {"v": 0.0}

    def monotonic() -> float:
        tick["v"] += 10.0
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    with pytest.raises(JobTimeoutError):
        poller.run("S", "1", interval=0, timeout=2)


@pytest.mark.asyncio
async def test_async_job_poller_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test asynchronous job polling timeout."""
    job = JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl="")
    get_job = AsyncMock(return_value=job)
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = AsyncJobPoller(get_job)

    tick = {"v": 0.0}

    def monotonic() -> float:
        tick["v"] += 10.0
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    with pytest.raises(JobTimeoutError):
        await poller.run("S", "1", interval=0, timeout=2)


def test_job_poller_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test synchronous job polling failure."""
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="FAILED", progress=10, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)

    with pytest.raises(JobFailedError) as exc_info:
        poller.run("S", "1", interval=0, timeout=5)
    assert exc_info.value.status.state == "FAILED"


@pytest.mark.asyncio
async def test_async_job_poller_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test asynchronous job polling failure."""
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="FAILED", progress=10, jobId="1", resultUrl=""),
    ]
    get_job = AsyncMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = AsyncJobPoller(get_job)

    with pytest.raises(JobFailedError) as exc_info:
        await poller.run("S", "1", interval=0, timeout=5)
    assert exc_info.value.status.state == "FAILED"


def test_run_on_progress_new_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test on_progress callback with JobStatusEvent signature."""
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)

    events = []

    def callback(event: JobStatusEvent) -> None:
        events.append(event)

    poller = JobPoller(get_job)
    poller.run("ST", "1", interval=0, on_progress=callback)

    assert len(events) == 2
    assert isinstance(events[0], JobStatusEvent)
    assert events[0].batch_id == "1"
    assert events[0].status.state == "PROCESSING"
    assert events[0].poll_number == 1
    assert events[0].is_terminal is False

    assert events[1].status.state == "COMPLETED"
    assert events[1].poll_number == 2
    assert events[1].is_terminal is True


def test_run_on_progress_deprecated_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test on_progress callback with deprecated (batch_id, status, elapsed) signature."""
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)

    calls = []

    def callback(batch_id, status, elapsed) -> None:
        calls.append((batch_id, status, elapsed))

    poller = JobPoller(get_job)
    poller.run("ST", "1", interval=0, on_progress=callback)

    assert len(calls) == 2
    assert calls[0][0] == "1"
    assert calls[0][1].state == "PROCESSING"
    assert isinstance(calls[0][2], float)


def test_poll_many_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test poll_many with multiple successful jobs."""
    jobs_states = {
        "1": [
            JobStatus(batchId="1", state="PROCESSING", progress=50, jobId="1", resultUrl=""),
            JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl=""),
        ],
        "2": [
            JobStatus(batchId="2", state="COMPLETED", progress=100, jobId="2", resultUrl=""),
        ],
    }

    def get_job(study_key, batch_id):
        return jobs_states[batch_id].pop(0)

    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)
    summary = poller.poll_many("ST", ["1", "2"], interval=0)

    assert summary.all_successful is True
    assert summary.any_failed is False
    assert len(summary.results) == 2
    assert summary.results["1"].state == "COMPLETED"
    assert summary.results["2"].state == "COMPLETED"
    assert len(summary.failures) == 0


def test_poll_many_with_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test poll_many where some jobs fail."""
    jobs_states = {
        "1": [JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl="")],
        "2": [JobStatus(batchId="2", state="FAILED", progress=0, jobId="2", resultUrl="")],
    }

    def get_job(study_key, batch_id):
        return jobs_states[batch_id].pop(0)

    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)
    summary = poller.poll_many("ST", ["1", "2"], interval=0)

    assert summary.all_successful is False
    assert summary.any_failed is True
    assert summary.results["1"].state == "COMPLETED"
    assert "2" not in summary.results
    assert len(summary.failures) == 1
    assert isinstance(summary.failures["2"], JobFailedError)


def test_poll_many_fail_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test poll_many with fail_fast=True."""

    def get_job(study_key, batch_id):
        if batch_id == "FAIL":
            raise ValueError("Immediate failure")
        return JobStatus(batchId="OK", state="COMPLETED", progress=100, jobId="2", resultUrl="")

    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)

    with pytest.raises(ValueError, match="Immediate failure"):
        poller.poll_many("ST", ["OK", "FAIL"], interval=0, fail_fast=True)


@pytest.mark.asyncio
async def test_async_poll_many_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test async_poll_many with multiple successful jobs."""
    jobs_states = {
        "1": [
            JobStatus(batchId="1", state="PROCESSING", progress=50, jobId="1", resultUrl=""),
            JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl=""),
        ],
        "2": [
            JobStatus(batchId="2", state="COMPLETED", progress=100, jobId="2", resultUrl=""),
        ],
    }

    async def get_job(study_key, batch_id):
        return jobs_states[batch_id].pop(0)

    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = AsyncJobPoller(get_job)
    summary = await poller.async_poll_many("ST", ["1", "2"], interval=0)

    assert summary.all_successful is True
    assert len(summary.results) == 2
    assert summary.results["1"].state == "COMPLETED"
    assert summary.results["2"].state == "COMPLETED"


def test_logging_output(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    """Test structured logging output."""
    states = [
        JobStatus(batchId="LOG", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="LOG", state="COMPLETED", progress=100, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)

    poller = JobPoller(get_job)
    with caplog.at_level(logging.DEBUG):
        poller.run("ST", "LOG", interval=0)

    assert "[JobPoller] batch_id=LOG state=PROCESSING progress=10% elapsed=" in caplog.text
    assert "[JobPoller] batch_id=LOG COMPLETED after 2 polls" in caplog.text


def test_logging_error(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    """Test logging output on failure."""
    states = [
        JobStatus(batchId="ERR", state="FAILED", progress=0, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)

    poller = JobPoller(get_job)
    with caplog.at_level(logging.DEBUG):
        try:
            poller.run("ST", "ERR", interval=0)
        except JobFailedError:
            pass

    assert "[JobPoller] batch_id=ERR FAILED: state=FAILED" in caplog.text


def test_job_status_event_immutable() -> None:
    """Test that JobStatusEvent is frozen."""
    status = JobStatus(batchId="1", state="COMPLETED", progress=100, jobId="1", resultUrl="")
    event = JobStatusEvent(
        batch_id="1", status=status, poll_number=1, elapsed=1.0, is_terminal=True
    )
    with pytest.raises(AttributeError):
        event.poll_number = 2  # type: ignore
