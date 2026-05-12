from __future__ import annotations

from typing import List, Optional

import typer
from rich import print

from imednet.cli.decorators import with_sdk
from imednet.cli.utils import STUDY_KEY_ARG, parse_filter_args
from imednet.sdk import ImednetSDK

from .data_extraction import DataExtractionWorkflow
from .subject_data import SubjectDataWorkflow

app = typer.Typer(name="workflows", help="Execute common data workflows.")


@app.command("extract-records")
@with_sdk
def extract_records(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    record_filter: Optional[List[str]] = typer.Option(
        None,
        "--record-filter",
        help=("Record filter criteria (e.g., 'form_key=DEMOG'). " "Repeat for multiple filters."),
    ),
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--subject-filter",
        help=(
            "Subject filter criteria (e.g., 'subject_status=Screened'). "
            "Repeat for multiple filters."
        ),
    ),
    visit_filter: Optional[List[str]] = typer.Option(
        None,
        "--visit-filter",
        help=("Visit filter criteria (e.g., 'visit_key=SCREENING'). " "Repeat for multiple filters."),
    ),
) -> None:
    """Extract records based on criteria spanning subjects, visits, and records."""
    workflow = DataExtractionWorkflow(sdk)

    parsed_record_filter = parse_filter_args(record_filter)
    parsed_subject_filter = parse_filter_args(subject_filter)
    parsed_visit_filter = parse_filter_args(visit_filter)

    print(f"Extracting records for study '{study_key}'...")
    records = workflow.extract_records_by_criteria(
        study_key=study_key,
        record_filter=parsed_record_filter,
        subject_filter=parsed_subject_filter,
        visit_filter=parsed_visit_filter,
    )

    if records:
        print(f"Found {len(records)} matching records:")
        print(records)
    else:
        print("No records found matching the criteria.")


@with_sdk
def subject_data(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    subject_key: str = typer.Argument(..., help="The key identifying the subject."),
) -> None:
    """Retrieve all data for a single subject."""
    workflow = SubjectDataWorkflow(sdk)
    data = workflow.get_all_subject_data(study_key, subject_key)
    print(data.model_dump())
