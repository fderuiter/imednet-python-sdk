from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..core.exceptions import JobTimeoutError

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..models.jobs import JobStatus
    from ..sdk import ImednetSDK


TERMINAL_JOB_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


class JobPoller:
    """Poll a job until it reaches a terminal state or times out."""

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

    def wait(self) -> "JobStatus":
        """Block until the job completes or raise :class:`JobTimeoutError`."""
        start = time.monotonic()
        while True:
            status = self._sdk.jobs.get(self._study_key, self._job_id)
            if status.state.upper() in TERMINAL_JOB_STATES:
                return status
            if time.monotonic() - start >= self._timeout:
                raise JobTimeoutError(
                    f"Timeout ({self._timeout}s) waiting for job '{self._job_id}' to complete."
                )
            time.sleep(self._interval)
