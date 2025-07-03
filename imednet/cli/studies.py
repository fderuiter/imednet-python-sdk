from __future__ import annotations

import typer
from rich import print

from ..sdk import ImednetSDK
from .decorators import with_sdk

app = typer.Typer(name="studies", help="Manage studies.")


@app.command("list")
@with_sdk
def list_studies(sdk: ImednetSDK) -> None:
    """List available studies."""
    print("Fetching studies...")
    studies_list = sdk.studies.list()
    if studies_list:
        print(studies_list)
    else:
        print("No studies found.")
