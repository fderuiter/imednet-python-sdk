from __future__ import annotations

import typer
from rich import print

from ..sdk import ImednetSDK
from .decorators import with_sdk

app = typer.Typer(name="sites", help="Manage sites within a study.")


@app.command("list")
@with_sdk
def list_sites(
    sdk: ImednetSDK,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List sites for a specific study."""
    print(f"Fetching sites for study '{study_key}'...")
    sites_list = sdk.sites.list(study_key)
    if sites_list:
        print(sites_list)
    else:
        print("No sites found for this study.")
