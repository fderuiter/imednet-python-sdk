from __future__ import annotations

import typer
from rich import print

from ..core.exceptions import ApiError

app = typer.Typer(name="queries", help="Manage queries within a study.")


@app.command("list")
def list_queries(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List queries for a study."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        print(f"Fetching queries for study '{study_key}'...")
        queries = sdk.queries.list(study_key)
        if queries:
            print(f"Found {len(queries)} queries:")
            print(queries)
        else:
            print("No queries found.")
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
