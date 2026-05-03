import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.models.jobs import JobStatus
from imednet.workflows.job_poller import AsyncJobPoller, JobPoller, JobTimeoutError


def test_job_poller_success(monkeypatch: pytest.MonkeyPatch) -> None:
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
    job = JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl="")
    get_job = MagicMock(return_value=job)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)

    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    with pytest.raises(JobTimeoutError):
        poller.run("S", "1", interval=0, timeout=2)


@pytest.mark.asyncio
async def test_async_job_poller_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    job = JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl="")
    get_job = AsyncMock(return_value=job)
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = AsyncJobPoller(get_job)

    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    with pytest.raises(JobTimeoutError):
        await poller.run("S", "1", interval=0, timeout=2)


def test_job_poller_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="FAILED", progress=10, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)

    with pytest.raises(RuntimeError):
        poller.run("S", "1", interval=0, timeout=5)


@pytest.mark.asyncio
async def test_async_job_poller_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=10, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="FAILED", progress=10, jobId="1", resultUrl=""),
    ]
    get_job = AsyncMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = AsyncJobPoller(get_job)

    with pytest.raises(RuntimeError):
        await poller.run("S", "1", interval=0, timeout=5)


def test_job_poller_cancelled(monkeypatch: pytest.MonkeyPatch) -> None:
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=50, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="CANCELLED", progress=50, jobId="1", resultUrl=""),
    ]
    get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *_: None)
    poller = JobPoller(get_job)
    result = poller.run("ST", "1", interval=0, timeout=5)
    assert result.state == "CANCELLED"


@pytest.mark.asyncio
async def test_async_job_poller_cancelled(monkeypatch: pytest.MonkeyPatch) -> None:
    states = [
        JobStatus(batchId="1", state="PROCESSING", progress=50, jobId="1", resultUrl=""),
        JobStatus(batchId="1", state="CANCELLED", progress=50, jobId="1", resultUrl=""),
    ]
    get_job = AsyncMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = AsyncJobPoller(get_job)
    result = await poller.run("ST", "1", interval=0, timeout=5)
    assert result.state == "CANCELLED"
