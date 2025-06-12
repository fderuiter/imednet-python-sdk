"""Utility helpers for working with background jobs."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from ..models import Job
    from ..sdk import ImednetSDK


TERMINAL_JOB_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


def wait_for_job(
    sdk: "ImednetSDK",
    study_key: str,
    batch_id: str,
    *,
    timeout: int = 300,
    poll_interval: int = 5,
) -> "Job":
    """Wait for a background job to reach a terminal state.

    Poll ``sdk.jobs.get`` until the returned job state is one of
    :data:`TERMINAL_JOB_STATES` or until ``timeout`` seconds elapse.

    Args:
        sdk: Instance of :class:`~imednet.sdk.ImednetSDK`.
        study_key: Study identifier.
        batch_id: Job batch identifier.
        timeout: Maximum time in seconds to wait.
        poll_interval: Seconds between polling attempts.

    Returns:
        The final :class:`~imednet.models.jobs.Job` status.

    Raises:
        TimeoutError: If the job does not reach a terminal state within ``timeout``.
    """
    start = time.monotonic()
    while True:
        job = sdk.jobs.get(study_key, batch_id)
        if job.state.upper() in TERMINAL_JOB_STATES:
            return job
        if time.monotonic() - start >= timeout:
            raise TimeoutError(
                f"Timeout ({timeout}s) waiting for job batch '{batch_id}' to complete. "
                f"Last state: {job.state}"
            )
        time.sleep(poll_interval)
