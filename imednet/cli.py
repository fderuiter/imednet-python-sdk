import json
import os
from typing import Union  # Import Union

import typer
from dotenv import load_dotenv
from rich import print

# Keep existing Any, Dict, List, Optional imports
from typing_extensions import Any, Dict, List, Optional

from .core.exceptions import ApiError
from .sdk import ImednetSDK

# Import the public filter utility
from .utils.filters import build_filter_string
from .workflows.credential_validation import CredentialValidationWorkflow
from .workflows.data_extraction import DataExtractionWorkflow
from .workflows.job_monitoring import JobMonitoringWorkflow
from .workflows.query_management import QueryManagementWorkflow
from .workflows.record_mapper import RecordMapper
from .workflows.record_update import RecordUpdateWorkflow
from .workflows.register_subjects import RegisterSubjectsWorkflow
from .workflows.site_progress import SiteProgressWorkflow
from .workflows.study_structure import get_study_structure
from .workflows.subject_data import SubjectDataWorkflow

# Load environment variables from .env file if it exists
load_dotenv()

app = typer.Typer(help="iMednet SDK Command Line Interface")

# Study key option used across commands
STUDY_KEY_OPTION = typer.Option(
    None,
    "--study-key",
    envvar="IMEDNET_STUDY_KEY",
    help="The key identifying the study."
    " Can also be set with the IMEDNET_STUDY_KEY environment variable.",
)


def require_study_key(study_key: Optional[str]) -> str:
    """Return the provided study key or exit if missing."""
    if not study_key:
        print(
            "[bold red]Error:[/bold red] IMEDNET_STUDY_KEY environment variable "
            "not set and --study-key was not provided."
        )
        raise typer.Exit(code=1)
    return study_key


# --- State Management ---
# Store SDK instance globally for reuse within commands if needed,
# initialized via callback.
state = {"sdk": None}


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


# Change input type hint to Optional[List[str]]
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
            # This assignment is now valid due to Union type hint
            filter_dict[key.strip()] = int(value)
        else:
            # This assignment is now valid due to Union type hint
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


# --- Sites Commands ---
sites_app = typer.Typer(name="sites", help="Manage sites within a study.")
app.add_typer(sites_app)


@sites_app.command("list")
def list_sites(
    study_key: Optional[str] = STUDY_KEY_OPTION,
):
    """List sites for a specific study."""
    study_key = require_study_key(study_key)
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


# --- Subjects Commands ---
subjects_app = typer.Typer(name="subjects", help="Manage subjects within a study.")
app.add_typer(subjects_app)


@subjects_app.command("list")
def list_subjects(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter criteria (e.g., 'subject_status=Screened'). " "Repeat for multiple filters.",
    ),
):
    """List subjects for a specific study, with optional filtering."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    try:
        # parse_filter_args now correctly accepts Optional[List[str]]
        parsed_filter = parse_filter_args(subject_filter)
        # Use the imported public build_filter_string utility
        filter_str = build_filter_string(parsed_filter) if parsed_filter else None

        print(f"Fetching subjects for study '{study_key}'...")
        list_kwargs = {"filter": filter_str} if filter_str else {}
        subjects_list = sdk.subjects.list(study_key, **list_kwargs)
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


# --- Workflows Commands ---
# Store workflow-related commands under a 'workflows' subcommand group.
workflows_app = typer.Typer(name="workflows", help="Execute common data workflows.")
app.add_typer(workflows_app)


@workflows_app.command("extract-records")
def extract_records(
    study_key: Optional[str] = STUDY_KEY_OPTION,
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
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = DataExtractionWorkflow(sdk)

    try:
        # parse_filter_args now correctly accepts Optional[List[str]]
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


@workflows_app.command("extract-audit-trail")
def extract_audit_trail(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    start_date: Optional[str] = typer.Option(None, help="Filter start date"),
    end_date: Optional[str] = typer.Option(None, help="Filter end date"),
    user_filter: Optional[List[str]] = typer.Option(
        None,
        "--user-filter",
        help="User filter criteria (e.g., 'user_id=5'). Repeat for multiple filters.",
    ),
):
    """Extract record revision audit trail."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = DataExtractionWorkflow(sdk)

    try:
        parsed_user_filter = parse_filter_args(user_filter)
        revisions = workflow.extract_audit_trail(
            study_key,
            start_date=start_date,
            end_date=end_date,
            user_filter=parsed_user_filter,
        )
        print(revisions)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("wait-for-job")
def wait_for_job(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    batch_id: str = typer.Argument(..., help="Job batch identifier"),
    timeout: int = typer.Option(300, help="Seconds to wait before timing out"),
    poll_interval: int = typer.Option(5, help="Seconds between polls"),
):
    """Wait for a background job to complete."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = JobMonitoringWorkflow(sdk)

    try:
        job = workflow.wait_for_job(
            study_key,
            batch_id,
            timeout=timeout,
            poll_interval=poll_interval,
        )
        print(job)
    except TimeoutError as exc:
        print(f"[bold red]Timeout:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("open-queries")
def open_queries(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    additional_filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Additional filter criteria. Repeat for multiple filters.",
    ),
):
    """List open queries for a study."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = QueryManagementWorkflow(sdk)

    try:
        parsed_filter = parse_filter_args(additional_filter)
        queries = workflow.get_open_queries(study_key, additional_filter=parsed_filter)
        print(queries)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("site-progress")
def site_progress(study_key: Optional[str] = STUDY_KEY_OPTION):
    """Show site progress metrics."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = SiteProgressWorkflow(sdk)

    try:
        results = workflow.get_site_progress(study_key)
        print(results)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("record-dataframe")
def record_dataframe(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    visit_key: Optional[str] = typer.Option(None, help="Optional visit key"),
    use_labels_as_columns: bool = typer.Option(True, help="Use variable labels"),
):
    """Output records as a CSV string."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = RecordMapper(sdk)

    try:
        df = workflow.dataframe(
            study_key, visit_key=visit_key, use_labels_as_columns=use_labels_as_columns
        )
        print(df.to_csv(index=False))
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("subject-data")
def subject_data(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    subject_key: str = typer.Argument(..., help="Subject key"),
):
    """Retrieve all data related to a subject."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = SubjectDataWorkflow(sdk)

    try:
        result = workflow.get_all_subject_data(study_key, subject_key)
        print(result)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("validate")
def validate_credentials(study_key: Optional[str] = STUDY_KEY_OPTION):
    """Validate API credentials against a study key."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = CredentialValidationWorkflow(sdk)

    try:
        valid = workflow.validate(study_key)
        print(valid)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("register-subjects")
def register_subjects(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    subjects_file: str = typer.Argument(..., help="Path to JSON file of subjects"),
    email_notify: Optional[str] = typer.Option(None, help="Notification email"),
):
    """Register multiple subjects from a JSON file."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = RegisterSubjectsWorkflow(sdk)

    try:
        with open(subjects_file, "r", encoding="utf-8") as f:
            subjects = json.load(f)
        result = workflow.register_subjects(study_key, subjects, email_notify=email_notify)
        print(result)
    except FileNotFoundError:
        print(f"[bold red]File not found:[/bold red] {subjects_file}")
        raise typer.Exit(code=1)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("submit-record-batch")
def submit_record_batch(
    study_key: Optional[str] = STUDY_KEY_OPTION,
    batch_file: str = typer.Argument(..., help="Path to JSON batch file"),
    wait_for_completion: bool = typer.Option(False, help="Wait for job to finish"),
):
    """Submit a batch of record updates from a JSON file."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()
    workflow = RecordUpdateWorkflow(sdk)

    try:
        with open(batch_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        job = workflow.submit_record_batch(
            study_key,
            data,
            wait_for_completion=wait_for_completion,
        )
        print(job)
    except FileNotFoundError:
        print(f"[bold red]File not found:[/bold red] {batch_file}")
        raise typer.Exit(code=1)
    except TimeoutError as exc:
        print(f"[bold red]Timeout:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("study-structure")
def study_structure(study_key: Optional[str] = STUDY_KEY_OPTION):
    """Retrieve the study structure definition."""
    study_key = require_study_key(study_key)
    sdk = get_sdk()

    try:
        struct = get_study_structure(sdk, study_key)
        print(struct)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Original Hello Command (can be removed or kept for testing) ---
@app.command()
def hello(name: str = "World"):
    """Says hello"""
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
