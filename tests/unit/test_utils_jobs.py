from unittest.mock import MagicMock

import pytest
from imednet.models.jobs import Job
from imednet.utils.jobs import wait_for_job


def test_wait_for_job_polls_until_terminal(monkeypatch) -> None:
    sdk = MagicMock()
    processing = Job(batch_id="1", state="PROCESSING")
    completed = Job(batch_id="1", state="COMPLETED")
    sdk.jobs.get.side_effect = [processing, completed]

    monkeypatch.setattr("imednet.utils.jobs.time.sleep", lambda *args: None)

    job = wait_for_job(sdk, "STUDY", "1", timeout=5, poll_interval=0)

    assert job is completed
    assert sdk.jobs.get.call_count == 2
    for call in sdk.jobs.get.call_args_list:
        assert call.args == ("STUDY", "1")


def test_wait_for_job_timeout(monkeypatch) -> None:
    sdk = MagicMock()
    sdk.jobs.get.return_value = Job(batch_id="1", state="PROCESSING")

    times = iter([0, 1, 2, 3, 4, 5])
    monkeypatch.setattr("imednet.utils.jobs.time.monotonic", lambda: next(times))
    monkeypatch.setattr("imednet.utils.jobs.time.sleep", lambda *args: None)

    with pytest.raises(TimeoutError):
        wait_for_job(sdk, "STUDY", "1", timeout=5, poll_interval=0)
