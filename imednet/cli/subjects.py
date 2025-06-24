from __future__ import annotations

from typing import List, Optional

import typer
from rich import print

from ..core.exceptions import ApiError
from .utils import parse_filter_args

app = typer.Typer(name="subjects", help="Manage subjects within a study.")


@app.command("list")
def list_subjects(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help=("Filter criteria (e.g., 'subject_status=Screened'). " "Repeat for multiple filters."),
    ),
) -> None:
    """List subjects for a specific study."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        parsed_filter = parse_filter_args(subject_filter)

        print(f"Fetching subjects for study '{study_key}'...")
        subjects_list = sdk.subjects.list(study_key, **(parsed_filter or {}))
        if subjects_list:
            print(f"Found {len(subjects_list)} subjects:")
            print(subjects_list)
        else:
            print("No subjects found matching the criteria.")
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
