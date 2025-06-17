from __future__ import annotations

import typer
from rich import print

from ..core.exceptions import ApiError


def subject_data(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    subject_key: str = typer.Argument(..., help="The key identifying the subject."),
) -> None:
    """Retrieve all data for a single subject."""
    from . import SubjectDataWorkflow, get_sdk

    sdk = get_sdk()
    workflow = SubjectDataWorkflow(sdk)

    try:
        data = workflow.get_all_subject_data(study_key, subject_key)
        print(data.model_dump())
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
