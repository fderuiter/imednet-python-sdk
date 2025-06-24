from __future__ import annotations

import typer
from rich import print

from ..core.exceptions import ApiError

app = typer.Typer(name="variables", help="Manage variables within a study.")


@app.command("list")
def list_variables(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List variables for a study."""
    from . import get_sdk

    sdk = get_sdk()
    try:
        print(f"Fetching variables for study '{study_key}'...")
        variables = sdk.variables.list(study_key)
        if variables:
            print(f"Found {len(variables)} variables:")
            print(variables)
        else:
            print("No variables found.")
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
