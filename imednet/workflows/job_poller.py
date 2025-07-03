"""Utility for polling job status."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, cast

from ..models import JobStatus

TERMINAL_JOB_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


class JobTimeoutError(TimeoutError):
    """Raised when a job does not finish before the timeout."""


class JobPoller:
    """Poll a job until it reaches a terminal state."""

    def __init__(
        self,
        get_job: Callable[[str, str], Any],
        is_async: bool,
    ) -> None:
        self._get_job = get_job
        self._async = is_async

    def _check_complete(self, status: JobStatus, batch_id: str) -> JobStatus:
        if status.state.upper() in TERMINAL_JOB_STATES:
            if status.state.upper() == "FAILED":
                raise RuntimeError(f"Job {batch_id} failed")
            return status
        return status

    def run(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Synchronously poll a job until completion."""

        if self._async:
            raise RuntimeError("Use run_async for asynchronous polling")

        start = time.monotonic()
        status = cast(JobStatus, self._get_job(study_key, batch_id))
        status = self._check_complete(status, batch_id)
        while status.state.upper() not in TERMINAL_JOB_STATES:
            if time.monotonic() - start >= timeout:
                raise JobTimeoutError(f"Timeout ({timeout}s) waiting for job {batch_id}")
            time.sleep(interval)
            status = cast(JobStatus, self._get_job(study_key, batch_id))
            status = self._check_complete(status, batch_id)
        return status

    async def run_async(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Asynchronously poll a job until completion."""

        if not self._async:
            raise RuntimeError("Use run for synchronous polling")

        start = time.monotonic()
        status = cast(JobStatus, await self._get_job(study_key, batch_id))
        status = self._check_complete(status, batch_id)
        while status.state.upper() not in TERMINAL_JOB_STATES:
            if time.monotonic() - start >= timeout:
                raise JobTimeoutError(f"Timeout ({timeout}s) waiting for job {batch_id}")
            await asyncio.sleep(interval)
            status = cast(JobStatus, await self._get_job(study_key, batch_id))
            status = self._check_complete(status, batch_id)
        return status
