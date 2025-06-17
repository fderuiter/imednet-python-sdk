import pytest
from imednet import ImednetSDK
from imednet.models.jobs import JobStatus


def _create_sdk() -> ImednetSDK:
    return ImednetSDK(
        api_key="key",
        security_key="secret",
        base_url="https://example.com",
    )


def test_poll_job_success(monkeypatch) -> None:
    sdk = _create_sdk()
    states = [
        JobStatus(batch_id="1", state="PROCESSING", progress=10),
        JobStatus(batch_id="1", state="COMPLETED", progress=100),
    ]

    monkeypatch.setattr(sdk, "get_job", lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *a: None)
    result = sdk.poll_job("STUDY", "1", interval=0, timeout=5)
    assert result.state == "COMPLETED"


def test_poll_job_timeout(monkeypatch) -> None:
    sdk = _create_sdk()
    job = JobStatus(batch_id="1", state="PROCESSING")
    monkeypatch.setattr(sdk, "get_job", lambda s, b: job)

    t = {"v": 0}

    def fake_monotonic() -> int:
        t["v"] += 1
        return t["v"]

    monkeypatch.setattr("time.monotonic", fake_monotonic)
    monkeypatch.setattr("time.sleep", lambda *a: None)
    with pytest.raises(TimeoutError):
        sdk.poll_job("S", "1", interval=0, timeout=2)


def test_poll_job_failed(monkeypatch) -> None:
    sdk = _create_sdk()
    states = [
        JobStatus(batch_id="1", state="PROCESSING"),
        JobStatus(batch_id="1", state="FAILED"),
    ]
    monkeypatch.setattr(sdk, "get_job", lambda s, b: states.pop(0))
    monkeypatch.setattr("time.sleep", lambda *a: None)
    with pytest.raises(RuntimeError):
        sdk.poll_job("S", "1", interval=0, timeout=5)
