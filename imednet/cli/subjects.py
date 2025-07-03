from __future__ import annotations

from typing import List, Optional

import typer
from rich import print

from ..sdk import ImednetSDK
from .decorators import with_sdk
from .utils import parse_filter_args

app = typer.Typer(name="subjects", help="Manage subjects within a study.")


@app.command("list")
@with_sdk
def list_subjects(
    sdk: ImednetSDK,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help=("Filter criteria (e.g., 'subject_status=Screened'). " "Repeat for multiple filters."),
    ),
) -> None:
    """List subjects for a specific study."""
    parsed_filter = parse_filter_args(subject_filter)

    print(f"Fetching subjects for study '{study_key}'...")
    subjects_list = sdk.subjects.list(study_key, **(parsed_filter or {}))
    if subjects_list:
        print(f"Found {len(subjects_list)} subjects:")
        print(subjects_list)
    else:
        print("No subjects found matching the criteria.")
