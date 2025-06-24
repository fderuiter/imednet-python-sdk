from __future__ import annotations

import typer
from rich import print

from ..core.exceptions import ApiError

app = typer.Typer(name="studies", help="Manage studies.")


@app.command("list")
def list_studies() -> None:
    """List available studies."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        print("Fetching studies...")
        studies_list = sdk.studies.list()
        if studies_list:
            print(studies_list)
        else:
            print("No studies found.")
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
