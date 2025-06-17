"""Utility for polling job status."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..models import JobStatus

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ..sdk import ImednetSDK

TERMINAL_JOB_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


class JobTimeoutError(TimeoutError):
    """Raised when a job does not finish before the timeout."""


class JobPoller:
    """Poll a job until it reaches a terminal state."""

    def __init__(
        self,
        sdk: "ImednetSDK",
        study_key: str,
        job_id: str,
        *,
        timeout_s: int = 300,
        poll_interval_s: int = 5,
    ) -> None:
        self._sdk = sdk
        self._study_key = study_key
        self._job_id = job_id
        self._timeout = timeout_s
        self._interval = poll_interval_s

    def wait(self) -> JobStatus:
        """Block until the job completes or raise :class:`JobTimeoutError`."""
        start = time.monotonic()
        status = self._sdk.jobs.get(self._study_key, self._job_id)
        while status.state.upper() not in TERMINAL_JOB_STATES:
            if time.monotonic() - start >= self._timeout:
                raise JobTimeoutError(f"Timeout ({self._timeout}s) waiting for job {self._job_id}")
            time.sleep(self._interval)
            status = self._sdk.jobs.get(self._study_key, self._job_id)
        return status
