from __future__ import annotations

import typer
from rich import print

from ..sdk import ImednetSDK
from .decorators import with_sdk

app = typer.Typer(name="variables", help="Manage variables within a study.")


@app.command("list")
@with_sdk
def list_variables(
    sdk: ImednetSDK,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List variables for a study."""
    print(f"Fetching variables for study '{study_key}'...")
    variables = sdk.variables.list(study_key)
    if variables:
        print(f"Found {len(variables)} variables:")
        print(variables)
    else:
        print("No variables found.")
