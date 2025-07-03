from __future__ import annotations

import typer
from rich import print

from ..sdk import ImednetSDK
from .decorators import with_sdk

app = typer.Typer(name="record-revisions", help="Manage record revision history.")


@app.command("list")
@with_sdk
def list_record_revisions(
    sdk: ImednetSDK,
    study_key: str = typer.Argument(..., help="The key identifying the study."),
) -> None:
    """List record revisions for a study."""
    print(f"Fetching record revisions for study '{study_key}'...")
    revisions = sdk.record_revisions.list(study_key)
    if revisions:
        print(f"Found {len(revisions)} record revisions:")
        print(revisions)
    else:
        print("No record revisions found.")
