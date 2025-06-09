"""Utilities for monitoring asynchronous iMednet jobs."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Callable, Optional

from ..models import Job

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


class JobMonitoringWorkflow:
    """Workflow helper for polling job status until completion."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def wait_for_job(
        self,
        study_key: str,
        batch_id: str,
        *,
        timeout: int = 300,
        poll_interval: int = 5,
        notify: Optional[Callable[[Job], Any]] = None,
    ) -> Job:
        """Wait for a job to reach a terminal state.

        Args:
            study_key: Study identifier.
            batch_id: Batch identifier of the job.
            timeout: Maximum time in seconds to wait.
            poll_interval: Seconds between polling attempts.
            notify: Optional callback invoked with the latest ``Job`` after each poll.

        Returns:
            The final ``Job`` state.

        Raises:
            TimeoutError: If the job does not reach a terminal state before ``timeout``.
        """

        start = time.monotonic()
        while True:
            job = self._sdk.jobs.get(study_key, batch_id)
            if notify:
                notify(job)
            if job.state.upper() in TERMINAL_STATES:
                return job
            if time.monotonic() - start >= timeout:
                raise TimeoutError(
                    f"Timeout ({timeout}s) waiting for job '{batch_id}' to complete. "
                    f"Last state: {job.state}"
                )
            time.sleep(poll_interval)
