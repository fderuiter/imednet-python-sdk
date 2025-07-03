from __future__ import annotations

import typer
from rich import print

from ..sdk import ImednetSDK
from .decorators import with_sdk

app = typer.Typer(name="queries", help="Manage queries within a study.")


@app.command("list")
@with_sdk
def list_queries(
    sdk: ImednetSDK,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List queries for a study."""
    print(f"Fetching queries for study '{study_key}'...")
    queries = sdk.queries.list(study_key)
    if queries:
        print(f"Found {len(queries)} queries:")
        print(queries)
    else:
        print("No queries found.")
