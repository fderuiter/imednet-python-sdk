from __future__ import annotations

import time
from typing import TYPE_CHECKING

from imednet.core.exceptions import JobTimeoutError
from imednet.models import Job

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from imednet.sdk import ImednetSDK

TERMINAL_JOB_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


class JobPoller:
    """Utility class to wait for an asynchronous job to finish."""

    def __init__(
        self,
        sdk: "ImednetSDK",
        study_key: str,
        job_id: str,
        timeout_s: int = 300,
        poll_interval_s: int = 5,
    ) -> None:
        self._sdk = sdk
        self._study_key = study_key
        self._job_id = job_id
        self._timeout_s = timeout_s
        self._poll_interval_s = poll_interval_s

    def wait(self) -> Job:
        """Poll the job status until it reaches a terminal state or times out."""
        start_time = time.monotonic()
        status = self._sdk.jobs.get(self._study_key, self._job_id)
        while True:
            if status.state.upper() in TERMINAL_JOB_STATES:
                return status
            if time.monotonic() - start_time >= self._timeout_s:
                raise JobTimeoutError(
                    f"Timeout ({self._timeout_s}s) waiting for job '{self._job_id}' to complete."
                )
            time.sleep(self._poll_interval_s)
            status = self._sdk.jobs.get(self._study_key, self._job_id)
