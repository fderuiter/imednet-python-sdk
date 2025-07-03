import asyncio
from unittest.mock import AsyncMock

import pytest
from imednet.models.jobs import JobStatus
from imednet.workflows.job_poller import JobPoller, JobTimeoutError


@pytest.mark.asyncio
async def test_async_job_poller_success(monkeypatch) -> None:
    get_job = AsyncMock()
    states = [
        JobStatus(batch_id="1", state="PROCESSING", progress=10),
        JobStatus(batch_id="1", state="COMPLETED", progress=100),
    ]
    get_job.side_effect = lambda s, b: states.pop(0)
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    poller = JobPoller(get_job, True)
    result = await poller.run_async("STUDY", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


@pytest.mark.asyncio
async def test_async_job_poller_timeout(monkeypatch) -> None:
    get_job = AsyncMock(return_value=JobStatus(batch_id="1", state="PROCESSING"))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    poller = JobPoller(get_job, True)
    with pytest.raises(JobTimeoutError):
        await poller.run_async("S", "1", interval=0, timeout=2)


@pytest.mark.asyncio
async def test_async_job_poller_failed(monkeypatch) -> None:
    states = [
        JobStatus(batch_id="1", state="PROCESSING"),
        JobStatus(batch_id="1", state="FAILED"),
    ]
    get_job = AsyncMock(side_effect=lambda s, b: states.pop(0))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    poller = JobPoller(get_job, True)
    with pytest.raises(RuntimeError):
        await poller.run_async("S", "1", interval=0, timeout=5)
