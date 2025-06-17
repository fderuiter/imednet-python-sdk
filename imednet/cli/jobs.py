from __future__ import annotations

import typer
from rich import print

app = typer.Typer(name="jobs", help="Manage background jobs.")


@app.command("status")
def job_status(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    batch_id: str = typer.Argument(..., help="Job batch ID."),
) -> None:
    """Fetch a job's current status."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        job = sdk.get_job(study_key, batch_id)
        print(job.model_dump())
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)


@app.command("wait")
def job_wait(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    batch_id: str = typer.Argument(..., help="Job batch ID."),
    interval: int = typer.Option(5, help="Polling interval in seconds."),
    timeout: int = typer.Option(300, help="Maximum time to wait."),
) -> None:
    """Wait for a job to reach a terminal state."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        job = sdk.poll_job(study_key, batch_id, interval=interval, timeout=timeout)
        print(job.model_dump())
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
