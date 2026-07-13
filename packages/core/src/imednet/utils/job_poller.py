"""Utility for polling job status."""

from __future__ import annotations

import asyncio
import inspect
import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, cast, runtime_checkable

from imednet.spi.models import JobStatus

logger = logging.getLogger(__name__)


@runtime_checkable
class JobProgressCallback(Protocol):
    """Callable invoked on each poll cycle with the current job status.

    Parameters
    ----------
    batch_id : str
        The batch ID being polled.
    status : JobStatus
        The current status object from the jobs endpoint.
    elapsed : float
        Seconds elapsed since polling started for this job.
    """

    def __call__(
        self,
        batch_id: str,
        status: JobStatus,
        elapsed: float,
    ) -> None:
        """Invoke the progress callback."""
        ...


@dataclass(frozen=True)
class JobStatusEvent:
    """Structured event for job status updates."""

    batch_id: str
    status: JobStatus
    poll_number: int  # 1-based poll attempt count
    elapsed: float  # seconds since polling started
    is_terminal: bool  # shortcut: status.is_terminal


@dataclass
class JobPollSummary:
    """Aggregate result of polling multiple jobs."""

    study_key: str
    results: Dict[str, JobStatus]  # batch_id → final JobStatus
    failures: Dict[str, Exception]  # batch_id → exception (timeout or API error)
    elapsed_total: float

    @property
    def all_successful(self) -> bool:
        """Return True if all jobs were successful."""
        return not self.failures and all(cast(Any, s).is_successful for s in self.results.values())

    @property
    def any_failed(self) -> bool:
        """Return True if any job failed or timed out."""
        return bool(self.failures) or any(cast(Any, s).is_failed for s in self.results.values())


class JobTimeoutError(TimeoutError):
    """Raised when a job does not finish before the timeout."""


class JobFailedError(Exception):
    """Raised when a job completes with a FAILED or CANCELLED state."""

    def __init__(self, message: str, status: JobStatus) -> None:
        """Initialize the JobFailedError."""
        super().__init__(message)
        self.status = status


def evaluate_job_state(job: JobStatus) -> bool:
    """Evaluate a job's status.

    Returns:
        True if the job completed successfully.
        False if the job is still in progress.

    Raises:
        JobFailedError: If the job ended in a failed or cancelled state.
    """
    if getattr(job, "is_failed", False):
        batch_id = getattr(job, "batch_id", getattr(job, "batchId", "unknown"))
        raise JobFailedError(f"Job {batch_id} ended in state {job.state}", job)
    return getattr(job, "is_terminal", False)


class BaseJobPoller:
    """Base class for polling a job until it reaches a terminal state."""

    def _check_complete(self, status: JobStatus, batch_id: str) -> JobStatus:
        """Internal hook to check if the status is complete."""
        return status

    def _evaluate(
        self, start_time: float, timeout: float, batch_id: str, status: JobStatus
    ) -> bool:
        """Evaluate if the job is complete, returning True if terminal."""
        if getattr(status, "is_terminal", False):
            return True
        if time.monotonic() - start_time >= timeout:
            raise JobTimeoutError(f"Timeout ({timeout}s) waiting for job {batch_id}")
        return False

    def _process_fetch_result(self, status: JobStatus, res: Any) -> JobStatus:
        """Process the fetched result data and attach to the status object."""
        if hasattr(res, "json"):
            try:
                setattr(status, "results", res.json())
            except Exception:
                setattr(status, "results", getattr(res, "text", str(res)))
        else:
            setattr(status, "results", res)
        return status

    def _trigger_callback(
        self,
        on_progress: Optional[JobProgressCallback],
        event: JobStatusEvent,
    ) -> None:
        """Invoke the progress callback with signature detection."""
        if not on_progress:
            return

        sig = inspect.signature(on_progress)
        if len(sig.parameters) == 1:
            # New style: (event: JobStatusEvent)
            on_progress(event)  # type: ignore
        else:
            # Old style: (batch_id, status, elapsed)
            on_progress(event.batch_id, event.status, event.elapsed)


class JobPoller(BaseJobPoller):
    """Synchronously poll a job until completion."""

    def __init__(
        self,
        get_job: Callable[[str, str], JobStatus],
        fetch_result: Callable[[str], Any] | None = None,
    ) -> None:
        """Initialize the synchronous job poller.

        Args:
            get_job: Callable that takes study_key and batch_id and returns JobStatus.
            fetch_result: Optional callable to fetch the result data from the result URL.
        """
        self._get_job = get_job
        self._fetch_result = fetch_result

    def run(
        self,
        study_key: str,
        batch_id: str,
        interval: float = 5.0,
        timeout: float = 300.0,
        *,
        on_progress: Optional[JobProgressCallback] = None,
    ) -> JobStatus:
        """Synchronously poll a job until completion."""
        start = time.monotonic()
        poll_number = 0

        while True:
            poll_number += 1
            result = self._get_job(study_key, batch_id)
            status = self._check_complete(result, batch_id)
            elapsed = time.monotonic() - start
            is_terminal = self._evaluate(start, timeout, batch_id, status)

            event = JobStatusEvent(
                batch_id=batch_id,
                status=status,
                poll_number=poll_number,
                elapsed=elapsed,
                is_terminal=is_terminal,
            )

            # Structured logging
            logger.debug(
                "[JobPoller] batch_id=%s state=%s progress=%s%% elapsed=%ss",
                batch_id,
                status.state,
                getattr(status, "progress", 0),
                round(elapsed, 1),
            )

            self._trigger_callback(on_progress, event)

            if is_terminal:
                if cast(Any, status).is_successful:
                    logger.info(
                        "[JobPoller] batch_id=%s COMPLETED after %s polls (%ss)",
                        batch_id,
                        poll_number,
                        round(elapsed, 1),
                    )
                else:
                    logger.error(
                        "[JobPoller] batch_id=%s FAILED: state=%s",
                        batch_id,
                        status.state,
                    )

                if self._fetch_result and getattr(status, "result_url", None):
                    try:
                        res = self._fetch_result(status.result_url)  # type: ignore
                        self._process_fetch_result(status, res)
                    except Exception:
                        pass
                evaluate_job_state(status)
                return status

            time.sleep(interval)

    def poll_many(
        self,
        study_key: str,
        batch_ids: List[str],
        interval: float = 5.0,
        timeout: float = 300.0,
        *,
        on_progress: Optional[JobProgressCallback] = None,
        fail_fast: bool = False,
    ) -> JobPollSummary:
        """Poll multiple jobs concurrently using threading.

        Parameters
        ----------
        study_key : str
            The study key.
        batch_ids : List[str]
            The batch IDs to monitor.
        interval : float
            Seconds between poll cycles.
        timeout : float
            Seconds before a job is considered timed out.
        fail_fast : bool
            If True, raise JobTimeoutError as soon as any single job times out.
            If False (default), continue polling remaining jobs and collect all
            failures into JobPollSummary.failures.
        on_progress : Optional[JobProgressCallback]
            Called for each job on each poll cycle. Thread-safe: the callback
            must be safe to call from multiple threads simultaneously.
        """
        results: Dict[str, JobStatus] = {}
        failures: Dict[str, Exception] = {}
        lock = threading.Lock()
        start = time.monotonic()

        def _poll_one(batch_id: str) -> None:
            try:
                status = self.run(
                    study_key,
                    batch_id,
                    interval=interval,
                    timeout=timeout,
                    on_progress=on_progress,
                )
                with lock:
                    results[batch_id] = status
            except Exception as exc:
                with lock:
                    failures[batch_id] = exc
                # If fail_fast is true, we still let the thread exit gracefully.
                # The exception is raised in the main thread after joining.

        threads = [threading.Thread(target=_poll_one, args=(bid,)) for bid in batch_ids]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if fail_fast and failures:
            raise next(iter(failures.values()))

        return JobPollSummary(
            study_key=study_key,
            results=results,
            failures=failures,
            elapsed_total=time.monotonic() - start,
        )


class AsyncJobPoller(BaseJobPoller):
    """Asynchronously poll a job until completion."""

    def __init__(
        self,
        get_job: Callable[[str, str], Awaitable[JobStatus]],
        fetch_result: Callable[[str], Awaitable[Any]] | None = None,
    ) -> None:
        """Initialize the asynchronous job poller.

        Args:
            get_job: Awaitable callable that takes study_key and batch_id and returns JobStatus.
            fetch_result: Optional awaitable callable to fetch the result data.
        """
        self._get_job = get_job
        self._fetch_result = fetch_result

    async def run(
        self,
        study_key: str,
        batch_id: str,
        interval: float = 5.0,
        timeout: float = 300.0,
        *,
        on_progress: Optional[JobProgressCallback] = None,
    ) -> JobStatus:
        """Asynchronously poll a job until completion."""
        start = time.monotonic()
        poll_number = 0

        while True:
            poll_number += 1
            result = await self._get_job(study_key, batch_id)
            status = self._check_complete(result, batch_id)
            elapsed = time.monotonic() - start
            is_terminal = self._evaluate(start, timeout, batch_id, status)

            event = JobStatusEvent(
                batch_id=batch_id,
                status=status,
                poll_number=poll_number,
                elapsed=elapsed,
                is_terminal=is_terminal,
            )

            # Structured logging
            logger.debug(
                "[JobPoller] batch_id=%s state=%s progress=%s%% elapsed=%ss",
                batch_id,
                status.state,
                getattr(status, "progress", 0),
                round(elapsed, 1),
            )

            self._trigger_callback(on_progress, event)

            if is_terminal:
                if cast(Any, status).is_successful:
                    logger.info(
                        "[JobPoller] batch_id=%s COMPLETED after %s polls (%ss)",
                        batch_id,
                        poll_number,
                        round(elapsed, 1),
                    )
                else:
                    logger.error(
                        "[JobPoller] batch_id=%s FAILED: state=%s",
                        batch_id,
                        status.state,
                    )

                if self._fetch_result and getattr(status, "result_url", None):
                    try:
                        res = await self._fetch_result(status.result_url)  # type: ignore
                        self._process_fetch_result(status, res)
                    except Exception:
                        pass
                evaluate_job_state(status)
                return status

            await asyncio.sleep(interval)

    async def async_poll_many(
        self,
        study_key: str,
        batch_ids: List[str],
        interval: float = 5.0,
        timeout: float = 300.0,
        *,
        on_progress: Optional[JobProgressCallback] = None,
        fail_fast: bool = False,
    ) -> JobPollSummary:
        """Asynchronously poll multiple jobs concurrently via asyncio.gather.

        All jobs are polled in parallel. Results are collected regardless of
        individual failures unless fail_fast=True.
        """
        start = time.monotonic()
        results: Dict[str, JobStatus] = {}
        failures: Dict[str, Exception] = {}

        async def _poll_one(batch_id: str) -> None:
            try:
                status = await self.run(
                    study_key,
                    batch_id,
                    interval=interval,
                    timeout=timeout,
                    on_progress=on_progress,
                )
                results[batch_id] = status
            except Exception as exc:
                failures[batch_id] = exc
                if fail_fast:
                    raise

        # We use return_exceptions=not fail_fast so we can collect failures manually
        await asyncio.gather(
            *[_poll_one(bid) for bid in batch_ids], return_exceptions=not fail_fast
        )

        return JobPollSummary(
            study_key=study_key,
            results=results,
            failures=failures,
            elapsed_total=time.monotonic() - start,
        )
