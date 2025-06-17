from __future__ import annotations

import typer
from rich import print

from ..core.exceptions import ApiError

app = typer.Typer(name="sites", help="Manage sites within a study.")


@app.command("list")
def list_sites(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List sites for a specific study."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        print(f"Fetching sites for study '{study_key}'...")
        sites_list = sdk.sites.list(study_key)
        if sites_list:
            print(sites_list)
        else:
            print("No sites found for this study.")
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
