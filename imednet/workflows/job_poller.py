"""Utility for polling job status."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable, cast

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

    async def _run_common(
        self,
        study_key: str,
        batch_id: str,
        fetch_job: Callable[[], Awaitable[JobStatus]],
        sleep_fn: Callable[[int], Awaitable[Any]],
        interval: int,
        timeout: int,
    ) -> JobStatus:
        """Poll using provided callables until the job completes."""

        start = time.monotonic()
        status = await fetch_job()
        status = self._check_complete(status, batch_id)
        while status.state.upper() not in TERMINAL_JOB_STATES:
            if time.monotonic() - start >= timeout:
                raise JobTimeoutError(f"Timeout ({timeout}s) waiting for job {batch_id}")
            await sleep_fn(interval)
            status = await fetch_job()
            status = self._check_complete(status, batch_id)
        return status

    def run(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Synchronously poll a job until completion."""

        if self._async:
            raise RuntimeError("Use run_async for asynchronous polling")

        async def fetch_job() -> JobStatus:
            return cast(JobStatus, self._get_job(study_key, batch_id))

        async def sleep_fn(seconds: int) -> None:
            await asyncio.to_thread(time.sleep, seconds)

        return asyncio.run(
            self._run_common(
                study_key,
                batch_id,
                fetch_job,
                sleep_fn,
                interval,
                timeout,
            )
        )

    async def run_async(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Asynchronously poll a job until completion."""

        if not self._async:
            raise RuntimeError("Use run for synchronous polling")

        async def fetch_job() -> JobStatus:
            return cast(JobStatus, await self._get_job(study_key, batch_id))

        async def sleep_fn(seconds: int) -> None:
            await asyncio.sleep(seconds)

        return await self._run_common(
            study_key,
            batch_id,
            fetch_job,
            sleep_fn,
            interval,
            timeout,
        )
