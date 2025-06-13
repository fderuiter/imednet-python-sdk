import os
from pathlib import Path
from typing import Union  # Import Union

import pandas as pd
import typer
from dotenv import load_dotenv
from rich import print

# Keep existing Any, Dict, List, Optional imports
from typing_extensions import Any, Dict, List, Optional

from .core.exceptions import ApiError
from .integrations.export import (
    export_to_csv,
    export_to_excel,
    export_to_json,
    export_to_parquet,
    export_to_sql,
)
from .sdk import ImednetSDK

# Import the public filter utility
from .utils.filters import build_filter_string
from .workflows.data_extraction import DataExtractionWorkflow

# Load environment variables from .env file if it exists
load_dotenv()

app = typer.Typer(help="iMednet SDK Command Line Interface")


def get_sdk() -> ImednetSDK:
    """Initializes and returns the ImednetSDK instance using env vars."""
    api_key = os.getenv("IMEDNET_API_KEY")
    security_key = os.getenv("IMEDNET_SECURITY_KEY")
    base_url = os.getenv("IMEDNET_BASE_URL")  # Optional

    if not api_key or not security_key:
        print(
            "[bold red]Error:[/bold red] IMEDNET_API_KEY and "  # Line break
            "IMEDNET_SECURITY_KEY environment variables must be set."
        )
        raise typer.Exit(code=1)

    try:
        sdk = ImednetSDK(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url if base_url else None,
        )
        return sdk
    except Exception as e:
        # Print the exception directly, which often includes the message
        print(f"[bold red]Error initializing SDK:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.callback()
def main(ctx: typer.Context):
    """
    iMednet SDK CLI. Configure authentication via environment variables:
    IMEDNET_API_KEY, IMEDNET_SECURITY_KEY, [IMEDNET_BASE_URL]
    """
    # Eagerly initialize SDK to catch auth errors early,
    # but allow commands to potentially re-initialize if needed.
    # We don't store it in ctx.obj to avoid pickling issues if Typer internals change.
    # Instead, commands will call get_sdk().
    pass


def parse_filter_args(filter_args: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    """Parses a list of 'key=value' strings into a dictionary."""
    if not filter_args:  # Handle None input
        return None
    # Explicitly type the dictionary value to handle mixed types
    filter_dict: Dict[str, Union[str, bool, int]] = {}
    for arg in filter_args:
        if "=" not in arg:
            print(
                f"[bold red]Error:[/bold red] Invalid filter format: '{arg}'. " "Use 'key=value'."
            )
            raise typer.Exit(code=1)
        key, value = arg.split("=", 1)
        # Basic type inference (can be expanded)
        if value.lower() == "true":
            filter_dict[key.strip()] = True
        elif value.lower() == "false":
            filter_dict[key.strip()] = False
        elif value.isdigit():
            filter_dict[key.strip()] = int(value)
        else:
            filter_dict[key.strip()] = value
    return filter_dict


# --- Studies Commands ---
# Store studies commands under a 'studies' subcommand group.
studies_app = typer.Typer(name="studies", help="Manage studies.")
app.add_typer(studies_app)


@studies_app.command("list")
def list_studies():
    """List available studies."""
    sdk = get_sdk()
    try:
        print("Fetching studies...")
        studies_list = sdk.studies.list()
        if studies_list:
            print(studies_list)  # rich handles nice printing
        else:
            print("No studies found.")
    except ApiError as e:
        # Print the exception directly, which includes status and details
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Queries Commands ---
queries_app = typer.Typer(name="queries", help="Manage queries within a study.")
app.add_typer(queries_app)


@queries_app.command("list")
def list_queries(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List queries for a study."""
    sdk = get_sdk()
    try:
        print(f"Fetching queries for study '{study_key}'...")
        queries = sdk.queries.list(study_key)
        if queries:
            print(f"Found {len(queries)} queries:")
            print(queries)
        else:
            print("No queries found.")
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Variables Commands ---
variables_app = typer.Typer(name="variables", help="Manage variables within a study.")
app.add_typer(variables_app)


@variables_app.command("list")
def list_variables(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List variables for a study."""
    sdk = get_sdk()
    try:
        print(f"Fetching variables for study '{study_key}'...")
        variables = sdk.variables.list(study_key)
        if variables:
            print(f"Found {len(variables)} variables:")
            print(variables)
        else:
            print("No variables found.")
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Record Revisions Commands ---
record_revisions_app = typer.Typer(name="record-revisions", help="Manage record revision history.")
app.add_typer(record_revisions_app)


@record_revisions_app.command("list")
def list_record_revisions(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List record revisions for a study."""
    sdk = get_sdk()
    try:
        print(f"Fetching record revisions for study '{study_key}'...")
        revisions = sdk.record_revisions.list(study_key)
        if revisions:
            print(f"Found {len(revisions)} record revisions:")
            print(revisions)
        else:
            print("No record revisions found.")
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Sites Commands ---
sites_app = typer.Typer(name="sites", help="Manage sites within a study.")
app.add_typer(sites_app)


@sites_app.command("list")
def list_sites(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
):
    """List sites for a specific study."""
    sdk = get_sdk()
    try:
        print(f"Fetching sites for study '{study_key}'...")
        sites_list = sdk.sites.list(study_key)
        if sites_list:
            print(sites_list)
        else:
            print("No sites found for this study.")
    except ApiError as e:
        # Print the exception directly
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Export Commands ---
export_app = typer.Typer(name="export", help="Export study data to various formats.")
app.add_typer(export_app)


@export_app.command("parquet")
def export_parquet(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination Parquet file."),
) -> None:
    """Export study records to a Parquet file."""
    sdk = get_sdk()
    try:
        export_to_parquet(sdk, study_key, str(path))
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@export_app.command("csv")
def export_csv(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination CSV file."),
) -> None:
    """Export study records to a CSV file."""
    sdk = get_sdk()
    try:
        export_to_csv(sdk, study_key, str(path))
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@export_app.command("excel")
def export_excel(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination Excel workbook."),
) -> None:
    """Export study records to an Excel workbook."""
    sdk = get_sdk()
    try:
        export_to_excel(sdk, study_key, str(path))
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@export_app.command("json")
def export_json_cmd(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination JSON file."),
) -> None:
    """Export study records to a JSON file."""
    sdk = get_sdk()
    try:
        export_to_json(sdk, study_key, str(path))
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@export_app.command("sql")
def export_sql(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    table: str = typer.Argument(..., help="Destination table name."),
    connection_string: str = typer.Argument(..., help="Database connection string."),
) -> None:
    """Export study records to a SQL table."""
    sdk = get_sdk()
    try:
        export_to_sql(sdk, study_key, table, connection_string)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Subjects Commands ---
subjects_app = typer.Typer(name="subjects", help="Manage subjects within a study.")
app.add_typer(subjects_app)


@subjects_app.command("list")
def list_subjects(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter criteria (e.g., 'subject_status=Screened'). " "Repeat for multiple filters.",
    ),
):
    """List subjects for a specific study, with optional filtering."""
    sdk = get_sdk()
    try:
        parsed_filter = parse_filter_args(subject_filter)
        # Use the imported public build_filter_string utility
        filter_str = build_filter_string(parsed_filter) if parsed_filter else None

        print(f"Fetching subjects for study '{study_key}'...")
        subjects_list = sdk.subjects.list(study_key, filter=filter_str)
        if subjects_list:
            print(f"Found {len(subjects_list)} subjects:")
            print(subjects_list)
        else:
            print("No subjects found matching the criteria.")
    except ApiError as e:
        # Print the exception directly
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Jobs Commands ---
jobs_app = typer.Typer(name="jobs", help="Manage background jobs.")
app.add_typer(jobs_app)


@jobs_app.command("status")
def job_status(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    batch_id: str = typer.Argument(..., help="Job batch ID."),
):
    """Fetch a job's current status."""
    sdk = get_sdk()
    try:
        job = sdk.get_job(study_key, batch_id)
        print(job.model_dump())
    except Exception as e:  # Catch ApiError and others
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@jobs_app.command("wait")
def job_wait(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    batch_id: str = typer.Argument(..., help="Job batch ID."),
    interval: int = typer.Option(5, help="Polling interval in seconds."),
    timeout: int = typer.Option(300, help="Maximum time to wait."),
):
    """Wait for a job to reach a terminal state."""
    sdk = get_sdk()
    try:
        job = sdk.poll_job(study_key, batch_id, interval=interval, timeout=timeout)
        print(job.model_dump())
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Records Commands ---
records_app = typer.Typer(name="records", help="Manage records within a study.")
app.add_typer(records_app)


@records_app.command("list")
def list_records(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save records to the given format",
        show_choices=True,
        rich_help_panel="Output Options",
    ),
):
    """List records for a study."""
    sdk = get_sdk()
    try:
        if output and output.lower() not in {"json", "csv"}:
            print("[bold red]Invalid output format. Use 'json' or 'csv'.[/bold red]")
            raise typer.Exit(code=1)
        print(f"Fetching records for study '{study_key}'...")
        records = sdk.records.list(study_key)
        rows = [r.model_dump(by_alias=True) for r in records]
        df = pd.DataFrame(rows)

        if output:
            path = Path(f"records.{output}")
            if output == "csv":
                df.to_csv(path, index=False)
            else:
                df.to_json(path, orient="records", indent=2)
            print(f"Saved {len(df)} records to {path}")
        else:
            if df.empty:
                print("No records found.")
            else:
                print(df.head().to_string(index=False))
                if len(df) > 5:
                    print(f"... ({len(df)} total records)")
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Workflows Commands ---
# Store workflow-related commands under a 'workflows' subcommand group.
workflows_app = typer.Typer(name="workflows", help="Execute common data workflows.")
app.add_typer(workflows_app)


@workflows_app.command("extract-records")
def extract_records(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    record_filter: Optional[List[str]] = typer.Option(
        None,
        "--record-filter",
        help="Record filter criteria (e.g., 'form_key=DEMOG'). " "Repeat for multiple filters.",
    ),
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--subject-filter",
        help="Subject filter criteria (e.g., 'subject_status=Screened'). "
        "Repeat for multiple filters.",
    ),
    visit_filter: Optional[List[str]] = typer.Option(
        None,
        "--visit-filter",
        help="Visit filter criteria (e.g., 'visit_key=SCREENING'). " "Repeat for multiple filters.",
    ),
):
    """Extract records based on criteria spanning subjects, visits, and records."""
    sdk = get_sdk()
    workflow = DataExtractionWorkflow(sdk)

    try:
        parsed_record_filter = parse_filter_args(record_filter)
        parsed_subject_filter = parse_filter_args(subject_filter)
        parsed_visit_filter = parse_filter_args(visit_filter)

        print(f"Extracting records for study '{study_key}'...")
        # Note: The workflow method expects dictionaries.
        records = workflow.extract_records_by_criteria(
            study_key=study_key,
            record_filter=parsed_record_filter,
            subject_filter=parsed_subject_filter,
            visit_filter=parsed_visit_filter,
        )

        if records:
            print(f"Found {len(records)} matching records:")
            print(records)  # rich handles nice printing of the list of Pydantic models
        else:
            print("No records found matching the criteria.")

    except ApiError as e:
        # Print the exception directly
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
