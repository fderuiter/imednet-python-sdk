import asyncio
from unittest.mock import AsyncMock

import pytest

import imednet.sdk as sdk_mod
from imednet.models.jobs import JobStatus


def _create_sdk(async_mode: bool) -> sdk_mod.ImednetSDK:
    cls = sdk_mod.AsyncImednetSDK if async_mode else sdk_mod.ImednetSDK
    return cls(api_key="key", security_key="secret", base_url="https://example.com")


@pytest.mark.parametrize("async_mode", [False, True])
def test_poll_job_success(async_mode: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk = _create_sdk(async_mode)
    states = [
        JobStatus(batch_id="1", state="PROCESSING", progress=10),
        JobStatus(batch_id="1", state="COMPLETED", progress=100),
    ]
    if async_mode:
        monkeypatch.setattr(
            sdk.jobs,
            "async_get",
            AsyncMock(side_effect=lambda s, b: states.pop(0)),
        )
        monkeypatch.setattr(asyncio, "sleep", AsyncMock())
        result = asyncio.run(sdk.async_poll_job("STUDY", "1", interval=0, timeout=5))
    else:
        monkeypatch.setattr(sdk.jobs, "get", lambda s, b: states.pop(0))
        monkeypatch.setattr("time.sleep", lambda *a: None)
        result = sdk.poll_job("STUDY", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


@pytest.mark.parametrize("async_mode", [False, True])
def test_poll_job_timeout(async_mode: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk = _create_sdk(async_mode)
    job = JobStatus(batch_id="1", state="PROCESSING")
    if async_mode:
        monkeypatch.setattr(
            sdk.jobs,
            "async_get",
            AsyncMock(return_value=job),
        )
        monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    else:
        monkeypatch.setattr(sdk.jobs, "get", lambda s, b: job)
        monkeypatch.setattr("time.sleep", lambda *a: None)
    tick = {"v": 0}

    def monotonic() -> int:
        tick["v"] += 1
        return tick["v"]

    monkeypatch.setattr("time.monotonic", monotonic)
    with pytest.raises(TimeoutError):
        if async_mode:
            asyncio.run(sdk.async_poll_job("S", "1", interval=0, timeout=2))
        else:
            sdk.poll_job("S", "1", interval=0, timeout=2)


@pytest.mark.parametrize("async_mode", [False, True])
def test_poll_job_failed(async_mode: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    sdk = _create_sdk(async_mode)
    states = [
        JobStatus(batch_id="1", state="PROCESSING"),
        JobStatus(batch_id="1", state="FAILED"),
    ]
    if async_mode:
        monkeypatch.setattr(
            sdk.jobs,
            "async_get",
            AsyncMock(side_effect=lambda s, b: states.pop(0)),
        )
        monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    else:
        monkeypatch.setattr(sdk.jobs, "get", lambda s, b: states.pop(0))
        monkeypatch.setattr("time.sleep", lambda *a: None)
    with pytest.raises(RuntimeError):
        if async_mode:
            asyncio.run(sdk.async_poll_job("S", "1", interval=0, timeout=5))
        else:
            sdk.poll_job("S", "1", interval=0, timeout=5)
