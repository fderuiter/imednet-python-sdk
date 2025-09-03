from __future__ import annotations

import typer
from rich import print

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG

app = typer.Typer(name="jobs", help="Manage background jobs.")


@app.command("status")
@with_sdk
def job_status(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    batch_id: str = typer.Argument(..., help="Job batch ID."),
) -> None:
    """Fetch and display the current status of a job.

    Args:
        sdk: The ImednetSDK instance.
        study_key: The key of the study.
        batch_id: The batch ID of the job.
    """
    job = sdk.get_job(study_key, batch_id)
    print(job.model_dump())


@app.command("wait")
@with_sdk
def job_wait(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    batch_id: str = typer.Argument(..., help="Job batch ID."),
    interval: int = typer.Option(5, help="Polling interval in seconds."),
    timeout: int = typer.Option(300, help="Maximum time to wait."),
) -> None:
    """Wait for a job to reach a terminal state and display its final status.

    Args:
        sdk: The ImednetSDK instance.
        study_key: The key of the study.
        batch_id: The batch ID of the job.
        interval: The polling interval in seconds.
        timeout: The maximum time to wait in seconds.
    """
    job = sdk.poll_job(study_key, batch_id, interval=interval, timeout=timeout)
    print(job.model_dump())
