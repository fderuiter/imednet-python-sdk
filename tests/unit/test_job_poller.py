import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.models.jobs import JobStatus
from imednet.workflows.job_poller import JobPoller, JobTimeoutError


@pytest.mark.parametrize("async_mode", [False, True])
def test_job_poller_success(async_mode: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    states = [
        JobStatus(batch_id="1", state="PROCESSING", progress=10),
        JobStatus(batch_id="1", state="COMPLETED", progress=100),
    ]
    if async_mode:
        get_job = AsyncMock(side_effect=lambda s, b: states.pop(0))
        monkeypatch.setattr(asyncio, "sleep", AsyncMock())
        poller = JobPoller(get_job, True)
        result = asyncio.run(poller.run_async("ST", "1", interval=0, timeout=5))
    else:
        get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
        monkeypatch.setattr("time.sleep", lambda *_: None)
        poller = JobPoller(get_job, False)
        result = poller.run("ST", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


@pytest.mark.parametrize("async_mode", [False, True])
def test_job_poller_timeout(async_mode: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    job = JobStatus(batch_id="1", state="PROCESSING")
    if async_mode:
        get_job = AsyncMock(return_value=job)
        monkeypatch.setattr(asyncio, "sleep", AsyncMock())
        poller = JobPoller(get_job, True)
    else:
        get_job = MagicMock(return_value=job)
        monkeypatch.setattr("time.sleep", lambda *_: None)
        poller = JobPoller(get_job, False)

    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    with pytest.raises(JobTimeoutError):
        if async_mode:
            asyncio.run(poller.run_async("S", "1", interval=0, timeout=2))
        else:
            poller.run("S", "1", interval=0, timeout=2)


@pytest.mark.parametrize("async_mode", [False, True])
def test_job_poller_failed(async_mode: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    states = [
        JobStatus(batch_id="1", state="PROCESSING"),
        JobStatus(batch_id="1", state="FAILED"),
    ]
    if async_mode:
        get_job = AsyncMock(side_effect=lambda s, b: states.pop(0))
        monkeypatch.setattr(asyncio, "sleep", AsyncMock())
        poller = JobPoller(get_job, True)
    else:
        get_job = MagicMock(side_effect=lambda s, b: states.pop(0))
        monkeypatch.setattr("time.sleep", lambda *_: None)
        poller = JobPoller(get_job, False)

    with pytest.raises(RuntimeError):
        if async_mode:
            asyncio.run(poller.run_async("S", "1", interval=0, timeout=5))
        else:
            poller.run("S", "1", interval=0, timeout=5)
