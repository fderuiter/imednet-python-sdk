from __future__ import annotations

from typing import List, Optional

import typer

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, display_list, echo_fetch, parse_filter_args

app = typer.Typer(name="subjects", help="Manage subjects within a study.")


@app.command("list")
@with_sdk
def list_subjects(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help=("Filter criteria (e.g., 'subject_status=Screened'). " "Repeat for multiple filters."),
    ),
) -> None:
    """List subjects for a specific study."""
    parsed_filter = parse_filter_args(subject_filter)

    echo_fetch("subjects", study_key)
    subjects_list = sdk.subjects.list(study_key, **(parsed_filter or {}))
    display_list(subjects_list, "subjects", "No subjects found matching the criteria.")
