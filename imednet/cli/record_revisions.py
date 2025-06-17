from __future__ import annotations

import typer
from rich import print

from ..core.exceptions import ApiError

app = typer.Typer(name="record-revisions", help="Manage record revision history.")


@app.command("list")
def list_record_revisions(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List record revisions for a study."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        print(f"Fetching record revisions for study '{study_key}'...")
        revisions = sdk.record_revisions.list(study_key)
        if revisions:
            print(f"Found {len(revisions)} record revisions:")
            print(revisions)
        else:
            print("No record revisions found.")
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
