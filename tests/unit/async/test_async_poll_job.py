import asyncio
from unittest.mock import AsyncMock

import pytest

from imednet.models.jobs import JobStatus
from imednet.sdk import AsyncImednetSDK


def _create_sdk() -> AsyncImednetSDK:
    return AsyncImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )


@pytest.mark.asyncio
async def test_async_poll_job_success(monkeypatch) -> None:
    sdk = _create_sdk()
    states = [
        JobStatus(batch_id="1", state="PROCESSING", progress=10),
        JobStatus(batch_id="1", state="COMPLETED", progress=100),
    ]
    monkeypatch.setattr(sdk.jobs, "async_get", AsyncMock(side_effect=lambda s, b: states.pop(0)))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    result = await sdk.async_poll_job("STUDY", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


@pytest.mark.asyncio
async def test_async_poll_job_timeout(monkeypatch) -> None:
    sdk = _create_sdk()
    job = JobStatus(batch_id="1", state="PROCESSING")
    monkeypatch.setattr(sdk.jobs, "async_get", AsyncMock(return_value=job))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    with pytest.raises(TimeoutError):
        await sdk.async_poll_job("S", "1", interval=0, timeout=2)


@pytest.mark.asyncio
async def test_async_poll_job_failed(monkeypatch) -> None:
    sdk = _create_sdk()
    states = [
        JobStatus(batch_id="1", state="PROCESSING"),
        JobStatus(batch_id="1", state="FAILED"),
    ]
    monkeypatch.setattr(sdk.jobs, "async_get", AsyncMock(side_effect=lambda s, b: states.pop(0)))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    with pytest.raises(RuntimeError):
        await sdk.async_poll_job("S", "1", interval=0, timeout=5)
