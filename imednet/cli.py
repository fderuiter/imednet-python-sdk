"""Command-line interface for the iMednet SDK."""

import json
import os
from pathlib import Path
from typing import Union

import typer
from dotenv import load_dotenv
from rich import print

# Keep existing Any, Dict, List, Optional imports
from typing_extensions import Any, Dict, List, Optional

from .core.exceptions import ApiError
from .credentials import (
    CREDENTIALS_FILE,
    resolve_credentials,
)
from .credentials import (
    save_credentials as store_creds,
)
from .models.records import RegisterSubjectRequest
from .sdk import ImednetSDK

# Import the public filter utility
from .utils.filters import build_filter_string
from .workflows.audit_aggregation import AuditAggregationWorkflow
from .workflows.coding_review import CodingReviewWorkflow
from .workflows.data_extraction import DataExtractionWorkflow
from .workflows.enrollment_dashboard import build_dashboard
from .workflows.query_aging import QueryAgingWorkflow
from .workflows.query_management import QueryManagementWorkflow
from .workflows.register_subjects import RegisterSubjectsWorkflow
from .workflows.site_performance import SitePerformanceWorkflow
from .workflows.subject_enrollment_dashboard import SubjectEnrollmentDashboard
from .workflows.visit_completion import VisitCompletionWorkflow
from .workflows.visit_tracking import VisitTrackingWorkflow

# Load environment variables from .env file if it exists
load_dotenv()

app = typer.Typer(help="iMednet SDK Command Line Interface")
credentials_app = typer.Typer(name="credentials", help="Manage stored credentials")
app.add_typer(credentials_app)


def get_sdk(ctx: typer.Context) -> ImednetSDK:
    """Initializes and caches the ImednetSDK instance using env vars."""
    if "sdk" in ctx.obj:
        return ctx.obj["sdk"]

    base_url = os.getenv("IMEDNET_BASE_URL", "https://edc.prod.imednetapi.com")
    try:
        api_key, security_key, study_key = resolve_credentials()
        if study_key:
            os.environ.setdefault("IMEDNET_STUDY_KEY", study_key)
    except RuntimeError as exc:
        print(
            "[bold red]Error:[/bold red] IMEDNET_API_KEY and IMEDNET_SECURITY_KEY"
            " environment variables must be set or store them using 'imednet"
            " credentials save'."
        )
        raise typer.Exit(code=1) from exc

    try:
        sdk = ImednetSDK(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
        )
        ctx.obj["sdk"] = sdk
        return sdk
    except Exception as e:
        print(f"[bold red]Error initializing SDK:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.callback()
def main(ctx: typer.Context) -> None:
    """
    iMednet SDK CLI. Configure authentication via environment variables:
    IMEDNET_API_KEY, IMEDNET_SECURITY_KEY, [IMEDNET_BASE_URL]
    """
    """Initialize Typer context object."""
    ctx.obj = {}


# Change input type hint to Optional[List[str]]
def parse_filter_args(filter_args: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    """Parses a list of 'key=value' strings into a dictionary."""
    if not filter_args:  # Handle None input
        return None
    # Explicitly type the dictionary value to handle mixed types
    filter_dict: Dict[str, Union[str, bool, int]] = {}
    for arg in filter_args:
        if "=" not in arg:
            print(f"[bold red]Error:[/bold red] Invalid filter format: '{arg}'. Use 'key=value'.")
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


@credentials_app.command("save")
def save_credentials_cmd() -> None:
    """Prompt for credentials and store them encrypted."""
    api_key = typer.prompt("x-api-key", hide_input=True)
    sec_key = typer.prompt("x-imn-security-key", hide_input=True)
    study_key = typer.prompt("STUDYKEY")
    study_name = typer.prompt("Study Name")
    password = typer.prompt("Encryption password", hide_input=True, confirmation_prompt=True)
    store_creds(api_key, sec_key, study_key, study_name, password)
    print(f"Credentials saved to {CREDENTIALS_FILE}")


# --- Studies Commands ---
# Store studies commands under a 'studies' subcommand group.
studies_app = typer.Typer(name="studies", help="Manage studies.")
app.add_typer(studies_app)


@studies_app.command("list")
def list_studies(ctx: typer.Context) -> None:
    """List available studies."""
    sdk = get_sdk(ctx)
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
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List sites for a specific study."""
    sdk = get_sdk(ctx)
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
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    subject_filter: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter criteria (e.g., 'subject_status=Screened'). Repeat for multiple filters.",
    ),
) -> None:
    """List subjects for a specific study, with optional filtering."""
    sdk = get_sdk(ctx)
    try:
        # parse_filter_args now correctly accepts Optional[List[str]]
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


# --- Users Commands ---
users_app = typer.Typer(name="users", help="Manage users within a study.")
app.add_typer(users_app)

# --- Queries Commands ---
queries_app = typer.Typer(name="queries", help="Manage data queries.")
app.add_typer(queries_app)


@queries_app.command("open")
def list_open_queries_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List open queries for a study."""
    sdk = get_sdk(ctx)
    workflow = QueryManagementWorkflow(sdk)
    try:
        queries = workflow.get_open_queries(study_key)
        if queries:
            print(queries)
        else:
            print("No open queries found.")
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@queries_app.command("counts")
def query_state_counts_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """Get query counts grouped by state for a study."""
    sdk = get_sdk(ctx)
    workflow = QueryManagementWorkflow(sdk)
    try:
        counts = workflow.get_query_state_counts(study_key)
        print(counts)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@users_app.command("list")
def list_users(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    include_inactive: bool = typer.Option(
        False,
        "--include-inactive",
        "-i",
        help="Include inactive users in the results.",
    ),
) -> None:
    """List users for a study."""
    sdk = get_sdk(ctx)
    try:
        users = sdk.users.list(study_key, include_inactive=include_inactive)
        if users:
            print(users)
        else:
            print("No users found.")
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
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    record_filter: Optional[List[str]] = typer.Option(
        None,
        "--record-filter",
        help="Record filter criteria (e.g., 'form_key=DEMOG'). Repeat for multiple filters.",
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
        help="Visit filter criteria (e.g., 'visit_key=SCREENING'). Repeat for multiple filters.",
    ),
) -> None:
    """Extract records based on criteria spanning subjects, visits, and records."""
    sdk = get_sdk(ctx)
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


@workflows_app.command("register-subjects")
def register_subjects_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    subjects_file: Path = typer.Argument(
        ..., help="Path to JSON file containing subject registration data."
    ),
    email_notify: Optional[str] = typer.Option(
        None,
        "--email-notify",
        help="Email address to notify when the job completes.",
    ),
) -> None:
    """Register new subjects for a study from a JSON file."""
    sdk = get_sdk(ctx)
    workflow = RegisterSubjectsWorkflow(sdk)
    try:
        with subjects_file.open() as fh:
            data = json.load(fh)
        subjects = [RegisterSubjectRequest.model_validate(d) for d in data]
        result = workflow.register_subjects(
            study_key=study_key, subjects=subjects, email_notify=email_notify
        )
        print(result)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("enrollment-dashboard")
def enrollment_dashboard_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    export_csv: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        help="Path to export the dashboard as CSV.",
    ),
) -> None:
    """Show enrollment dashboard summarizing sites and enrollment dates."""
    sdk = get_sdk(ctx)
    try:
        df = build_dashboard(sdk, study_key)
        if export_csv:
            df.to_csv(export_csv, index=False)
            print(f"Dashboard exported to {export_csv}")
        else:
            print(df)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("visit-completion")
def visit_completion_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    subject_key: str = typer.Argument(..., help="The key identifying the subject."),
) -> None:
    """Summarize visit completion for a subject."""
    sdk = get_sdk(ctx)
    workflow = VisitCompletionWorkflow(sdk)
    try:
        result = workflow.get_subject_progress(study_key, subject_key)
        print(result)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("query-aging")
def query_aging_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    buckets: Optional[List[int]] = typer.Option(
        None,
        "--bucket",
        "-b",
        help="Day thresholds for aging buckets (repeat for multiple).",
    ),
) -> None:
    """Show counts of open queries grouped by age buckets."""
    sdk = get_sdk(ctx)
    wf = QueryAgingWorkflow(sdk)
    try:
        summary = wf.aging_summary(study_key, buckets=buckets)
        print(summary)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("site-performance")
def site_performance_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    export_csv: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        help="Path to export the metrics as CSV.",
    ),
) -> None:
    """Summarize enrollment and query metrics for each site."""
    sdk = get_sdk(ctx)
    wf = SitePerformanceWorkflow(sdk)
    try:
        df = wf.get_site_metrics(study_key)
        if export_csv:
            df.to_csv(export_csv, index=False)
            print(f"Metrics exported to {export_csv}")
        else:
            print(df)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("subject-enrollment")
def subject_enrollment_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    export_csv: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        help="Path to export the dashboard as CSV.",
    ),
) -> None:
    """Summarize subject enrollment and dropout rates by site."""
    sdk = get_sdk(ctx)
    wf = SubjectEnrollmentDashboard(sdk)
    try:
        df = wf.build(study_key)
        if export_csv:
            df.to_csv(export_csv, index=False)
            print(f"Dashboard exported to {export_csv}")
        else:
            print(df)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("audit-summary")
def audit_summary_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    start_date: Optional[str] = typer.Option(None, "--start-date"),
    end_date: Optional[str] = typer.Option(None, "--end-date"),
) -> None:
    """Show counts of record revisions grouped by user."""
    sdk = get_sdk(ctx)
    wf = AuditAggregationWorkflow(sdk)
    try:
        summary = wf.summary_by_user(study_key, start_date=start_date, end_date=end_date)
        print(summary)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("visit-tracking")
def visit_tracking_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """Show visit completion summaries for all subjects."""
    sdk = get_sdk(ctx)
    wf = VisitTrackingWorkflow(sdk)
    try:
        summary = wf.summary_by_subject(study_key)
        print(summary)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@workflows_app.command("coding-issues")
def coding_issues_cmd(
    ctx: typer.Context,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    mode: str = typer.Option(
        "uncoded",
        "--mode",
        "-m",
        help="Issue type: 'uncoded' or 'inconsistent'.",
    ),
) -> None:
    """List uncoded or inconsistent codings for a study."""
    sdk = get_sdk(ctx)
    wf = CodingReviewWorkflow(sdk)
    try:
        if mode == "inconsistent":
            items = wf.get_inconsistent_codings(study_key)
        else:
            items = wf.get_uncoded_items(study_key)
        print(items)
    except ApiError as e:
        print(f"[bold red]API Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Original Hello Command (can be removed or kept for testing) ---
@app.command()
def hello(name: str = "World") -> None:
    """Says hello"""
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
