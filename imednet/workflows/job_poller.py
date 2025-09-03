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
        """Initializes the JobPoller.

        Args:
            get_job: A function that fetches the job status.
            is_async: `True` if the `get_job` function is asynchronous.
        """
        self._get_job = get_job
        self._async = is_async

    async def _run_common(
        self,
        study_key: str,
        batch_id: str,
        fetch_job: Callable[[str, str], Any],
        sleep_fn: Callable[[float], Any],
        interval: int,
        timeout: int,
    ) -> JobStatus:
        """Core polling logic shared by sync and async runners.

        Args:
            study_key: The key of the study.
            batch_id: The batch ID of the job to poll.
            fetch_job: The function to call to get the job status.
            sleep_fn: The function to call to pause between polls.
            interval: The polling interval in seconds.
            timeout: The total time to wait for the job to complete.

        Returns:
            The final job status.

        Raises:
            JobTimeoutError: If the job does not complete within the timeout.
            RuntimeError: If the job fails.
        """
        start = time.monotonic()
        result = fetch_job(study_key, batch_id)
        status = cast(JobStatus, await result) if self._async else cast(JobStatus, result)
        status = self._check_complete(status, batch_id)

        while status.state.upper() not in TERMINAL_JOB_STATES:
            if time.monotonic() - start >= timeout:
                raise JobTimeoutError(f"Timeout ({timeout}s) waiting for job {batch_id}")
            sleep_res = sleep_fn(interval)
            if self._async:
                await sleep_res
            result = fetch_job(study_key, batch_id)
            status = cast(JobStatus, await result) if self._async else cast(JobStatus, result)
            status = self._check_complete(status, batch_id)
        return status

    def _check_complete(self, status: JobStatus, batch_id: str) -> JobStatus:
        """Check if the job has completed and raise an error if it failed.

        Args:
            status: The current job status.
            batch_id: The batch ID of the job.

        Returns:
            The job status if it has not failed.

        Raises:
            RuntimeError: If the job has failed.
        """
        if status.state.upper() in TERMINAL_JOB_STATES:
            if status.state.upper() == "FAILED":
                raise RuntimeError(f"Job {batch_id} failed")
            return status
        return status

    def run(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Synchronously poll a job until it reaches a terminal state.

        Args:
            study_key: The key of the study.
            batch_id: The batch ID of the job to poll.
            interval: The polling interval in seconds.
            timeout: The total time to wait for the job to complete.

        Returns:
            The final job status.

        Raises:
            RuntimeError: If called on an async-configured poller.
        """
        if self._async:
            raise RuntimeError("Use run_async for asynchronous polling")
        return asyncio.run(
            self._run_common(
                study_key,
                batch_id,
                self._get_job,
                time.sleep,
                interval,
                timeout,
            )
        )

    async def run_async(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Asynchronously poll a job until it reaches a terminal state.

        Args:
            study_key: The key of the study.
            batch_id: The batch ID of the job to poll.
            interval: The polling interval in seconds.
            timeout: The total time to wait for the job to complete.

        Returns:
            The final job status.

        Raises:
            RuntimeError: If called on a sync-configured poller.
        """
        if not self._async:
            raise RuntimeError("Use run for synchronous polling")
        return await self._run_common(
            study_key,
            batch_id,
            self._get_job,
            asyncio.sleep,
            interval,
            timeout,
        )
