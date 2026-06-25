"""Cli module."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import typer
from rich import print

from imednet.spi.cli import STUDY_KEY_ARG, parse_filter_args, with_sdk
from imednet.spi.facade import ImednetFacade

from .data_extraction import DataExtractionWorkflow
from .state_ledger import ExtractionStateLedger
from .subject_data import SubjectDataWorkflow
from .sync_worker import SyncWorker, SyncWorkerConfig

app = typer.Typer(name="workflows", help="Execute common data workflows.")


@app.command("extract-records")
@with_sdk  # type: ignore
def extract_records(
    sdk: ImednetFacade,
    study_key: str = STUDY_KEY_ARG,
    record_filter: Optional[List[str]] = typer.Option(
        None,
        "--record-filter",
        help=("Record filter criteria (e.g., 'form_key=DEMOG'). Repeat for multiple filters."),
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
        help=("Visit filter criteria (e.g., 'visit_key=SCREENING'). Repeat for multiple filters."),
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


@with_sdk  # type: ignore
def subject_data(
    sdk: ImednetFacade,
    study_key: str = STUDY_KEY_ARG,
    subject_key: str = typer.Argument(..., help="The key identifying the subject."),
) -> None:
    """Retrieve all data for a single subject."""
    workflow = SubjectDataWorkflow(sdk)
    data = workflow.get_all_subject_data(study_key, subject_key)
    print(data.model_dump())


@app.command("sync-worker")
@with_sdk  # type: ignore
def sync_worker(
    sdk: ImednetFacade,
    study_key: str = STUDY_KEY_ARG,
    interval: int = typer.Option(900, "--interval", min=1, help="Polling interval in seconds."),
    once: bool = typer.Option(
        False,
        "--once",
        help="Run a single sync cycle and exit.",
    ),
) -> None:
    """Run an idempotent background cache refresh worker."""
    from .cached_loader import CachedRecordsLoader

    worker = SyncWorker(
        CachedRecordsLoader(sdk),
        config=SyncWorkerConfig(study_key=study_key, interval_seconds=interval),
    )

    if once:
        count = worker.run_once()
        print(f"[green]Synced {count} cached records for study '{study_key}'.[/green]")
        return

    print(
        f"[green]Starting sync worker for study '{study_key}' "
        f"(interval={interval}s). Press Ctrl+C to stop.[/green]"
    )
    try:
        worker.run_forever()
    except KeyboardInterrupt:  # pragma: no cover - signal handling
        worker.stop()
        print("[yellow]Sync worker termination requested. Exiting cleanly.[/yellow]")


state_app = typer.Typer(name="state", help="Manage high-water mark execution ledger state.")


@state_app.command("show")
def show_state(
    ledger_path: str = typer.Option(
        "/var/lib/imednet/pipeline_ledger.json",
        "--ledger-path",
        "-l",
        help="Path to the pipeline ledger JSON file.",
    ),
    study_key: Optional[str] = typer.Option(
        None,
        "--study-key",
        "-s",
        help="Filter the ledger by a specific study key.",
    ),
) -> None:
    """Show the current high-water mark records and stream metadata."""
    ledger = ExtractionStateLedger(ledger_path)
    try:
        state = ledger.read_state()
    except Exception as err:
        print(f"[red]Failed to read ledger from {ledger_path}: {err}[/red]")
        raise typer.Exit(code=1)

    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=f"iMednet Extraction Ledger ({ledger_path})")
    table.add_column("Study Key", style="cyan")
    table.add_column("Stream Name", style="magenta")
    table.add_column("Last Timestamp (UTC)", style="green")
    table.add_column("Records Processed", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Error Message", style="red")

    has_data = False
    for s_key, study_state in state.studies.items():
        if study_key and s_key != study_key:
            continue
        for stream_name, stream_state in study_state.streams.items():
            has_data = True
            table.add_row(
                s_key,
                stream_name,
                stream_state.last_timestamp.isoformat(),
                str(stream_state.records_processed),
                stream_state.last_run_status,
                stream_state.error_message or "",
            )

    if has_data:
        console.print(table)
    else:
        print("[yellow]No ledger entries found matching filters.[/yellow]")


@state_app.command("set")
def set_state(
    study_key: str = typer.Option(..., "--study-key", "-s", help="The study key."),
    stream: str = typer.Option(..., "--stream", "-m", help="The stream name."),
    timestamp: str = typer.Option(..., "--timestamp", "-t", help="The ISO-8601 timestamp (UTC)."),
    records_processed: int = typer.Option(
        0, "--records-processed", "-r", help="Number of records processed."
    ),
    ledger_path: str = typer.Option(
        "/var/lib/imednet/pipeline_ledger.json",
        "--ledger-path",
        "-l",
        help="Path to the pipeline ledger JSON file.",
    ),
) -> None:
    """Manually set a high-water mark timestamp for a study and stream."""
    try:
        normalized = timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
    except ValueError as err:
        print(f"[red]Invalid ISO timestamp format: {err}[/red]")
        raise typer.Exit(code=1)

    ledger = ExtractionStateLedger(ledger_path)
    try:
        ledger.set_last_timestamp(
            study_key=study_key,
            stream_name=stream,
            timestamp=dt,
            records_processed=records_processed,
            status="success",
        )
        print(
            f"[green]Successfully set high-water mark for '{study_key}' -> '{stream}' "
            f"to {dt.isoformat()}[/green]"
        )
    except Exception as err:
        print(f"[red]Failed to write ledger: {err}[/red]")
        raise typer.Exit(code=1)


@state_app.command("reset")
def reset_state(
    study_key: str = typer.Option(..., "--study-key", "-s", help="The study key."),
    stream: Optional[str] = typer.Option(
        None,
        "--stream",
        "-m",
        help="The stream name. If omitted, all streams for the study will be reset.",
    ),
    ledger_path: str = typer.Option(
        "/var/lib/imednet/pipeline_ledger.json",
        "--ledger-path",
        "-l",
        help="Path to the pipeline ledger JSON file.",
    ),
) -> None:
    """Reset (clear) high-water mark state for a study/stream."""
    ledger = ExtractionStateLedger(ledger_path)
    try:
        if stream:
            removed = ledger.delete_entry(study_key, stream)
            if removed:
                print(
                    f"[green]Successfully reset stream '{stream}' for study '{study_key}'.[/green]"
                )
            else:
                print(f"[yellow]No stream '{stream}' found for study '{study_key}'.[/yellow]")
                return
        else:
            removed = ledger.delete_entry(study_key)
            if removed:
                print(f"[green]Successfully reset all streams for study '{study_key}'.[/green]")
            else:
                print(f"[yellow]No state found for study '{study_key}'.[/yellow]")
                return
    except Exception as err:
        print(f"[red]Failed to reset ledger state: {err}[/red]")
        raise typer.Exit(code=1)


app.add_typer(state_app)
