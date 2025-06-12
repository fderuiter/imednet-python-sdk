"""Utilities for working with asynchronous jobs."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ..models.jobs import Job
    from ..sdk import ImednetSDK


TERMINAL_JOB_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


def wait_for_job(
    sdk: "ImednetSDK",
    study_key: str,
    batch_id: str,
    *,
    timeout: int = 300,
    poll_interval: int = 5,
) -> Job:
    """Poll ``sdk.jobs.get`` until the job reaches a terminal state.

    Args:
        sdk: SDK instance used to fetch job status.
        study_key: Study identifier.
        batch_id: Job batch ID.
        timeout: Maximum time in seconds to wait.
        poll_interval: Delay between polls in seconds.

    Returns:
        The final :class:`~imednet.models.jobs.Job` object.

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
                f"Timeout ({timeout}s) waiting for job batch '{batch_id}' to complete."
            )
        time.sleep(poll_interval)
