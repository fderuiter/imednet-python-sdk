"""Utility for polling job status."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable

from imednet.spi.constants import TERMINAL_JOB_STATES
from imednet.spi.models import JobStatus


class JobTimeoutError(TimeoutError):
    """Raised when a job does not finish before the timeout."""


class BaseJobPoller:
    """Base class for polling a job until it reaches a terminal state."""

    def _check_complete(self, status: JobStatus, batch_id: str) -> JobStatus:
        """TODO: Add docstring."""
        return status

    def _evaluate(self, start_time: float, timeout: int, batch_id: str, status: JobStatus) -> bool:
        """Evaluate if the job is complete, returning True if terminal."""
        if not status.state or status.state.upper() in TERMINAL_JOB_STATES:  # type: ignore
            return True
        if time.monotonic() - start_time >= timeout:
            raise JobTimeoutError(f"Timeout ({timeout}s) waiting for job {batch_id}")
        return False

    def _process_fetch_result(self, status: JobStatus, res: Any) -> JobStatus:
        """Process the fetched result data and attach to the status object."""
        if hasattr(res, "json"):
            try:
                setattr(status, 'results', res.json())
            except Exception:
                setattr(status, 'results', getattr(res, "text", str(res)))
        else:
            setattr(status, 'results', res)
        return status


class JobPoller(BaseJobPoller):
    """Synchronously poll a job until completion."""

    def __init__(
        self,
        get_job: Callable[[str, str], JobStatus],
        fetch_result: Callable[[str], Any] | None = None,
    ) -> None:
        """TODO: Add docstring."""
        self._get_job = get_job
        self._fetch_result = fetch_result

    def run(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Synchronously poll a job until completion."""
        start = time.monotonic()

        while True:
            result = self._get_job(study_key, batch_id)
            status = self._check_complete(result, batch_id)

            if self._evaluate(start, timeout, batch_id, status):
                if self._fetch_result and getattr(status, "result_url", None):
                    try:
                        res = self._fetch_result(status.result_url)  # type: ignore
                        self._process_fetch_result(status, res)
                    except Exception:
                        pass
                return status

            time.sleep(interval)


class AsyncJobPoller(BaseJobPoller):
    """Asynchronously poll a job until completion."""

    def __init__(
        self,
        get_job: Callable[[str, str], Awaitable[JobStatus]],
        fetch_result: Callable[[str], Awaitable[Any]] | None = None,
    ) -> None:
        """TODO: Add docstring."""
        self._get_job = get_job
        self._fetch_result = fetch_result

    async def run(
        self, study_key: str, batch_id: str, interval: int = 5, timeout: int = 300
    ) -> JobStatus:
        """Asynchronously poll a job until completion."""
        start = time.monotonic()

        while True:
            result = await self._get_job(study_key, batch_id)
            status = self._check_complete(result, batch_id)

            if self._evaluate(start, timeout, batch_id, status):
                if self._fetch_result and getattr(status, "result_url", None):
                    try:
                        res = await self._fetch_result(status.result_url)  # type: ignore
                        self._process_fetch_result(status, res)
                    except Exception:
                        pass
                return status

            await asyncio.sleep(interval)
