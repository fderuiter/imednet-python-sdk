"""Utility for polling job status."""

from __future__ import annotations

import asyncio
import time
from typing import Awaitable, Callable

from ..constants import TERMINAL_JOB_STATES
from ..models import JobStatus


class JobTimeoutError(TimeoutError):
    """Raised when a job does not finish before the timeout."""


class BaseJobPoller:
    """Base class for polling a job until it reaches a terminal state."""

    def _check_complete(self, status: JobStatus, batch_id: str) -> JobStatus:
        if status.state.upper() in TERMINAL_JOB_STATES:
            if status.state.upper() == "FAILED":
                raise RuntimeError(f"Job {batch_id} failed")
            return status
        return status

    def _check_timeout(self, start_time: float, timeout: int, batch_id: str) -> None:
        if time.monotonic() - start_time >= timeout:
            raise JobTimeoutError(f"Timeout ({timeout}s) waiting for job {batch_id}")


class JobPoller(BaseJobPoller):
    """Synchronously poll a job until completion."""

    def __init__(self, get_job: Callable[[str, str], JobStatus]) -> None:
        self._get_job = get_job

    def run(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Synchronously poll a job until completion."""
        start = time.monotonic()

        while True:
            result = self._get_job(study_key, batch_id)
            status = self._check_complete(result, batch_id)

            if status.state.upper() in TERMINAL_JOB_STATES:
                return status

            self._check_timeout(start, timeout, batch_id)
            time.sleep(interval)


class AsyncJobPoller(BaseJobPoller):
    """Asynchronously poll a job until completion."""

    def __init__(self, get_job: Callable[[str, str], Awaitable[JobStatus]]) -> None:
        self._get_job = get_job

    async def run(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Asynchronously poll a job until completion."""
        start = time.monotonic()

        while True:
            result = await self._get_job(study_key, batch_id)
            status = self._check_complete(result, batch_id)

            if status.state.upper() in TERMINAL_JOB_STATES:
                return status

            self._check_timeout(start, timeout, batch_id)
            await asyncio.sleep(interval)
