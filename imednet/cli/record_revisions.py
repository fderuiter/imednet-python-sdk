from __future__ import annotations

import typer

from ..sdk import ImednetSDK
from .decorators import with_sdk
from .utils import STUDY_KEY_ARG, display_list, echo_fetch

app = typer.Typer(name="record-revisions", help="Manage record revision history.")


@app.command("list")
@with_sdk
def list_record_revisions(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
) -> None:
    """List record revisions for a study."""
    echo_fetch("record revisions", study_key)
    revisions = sdk.record_revisions.list(study_key)
    display_list(revisions, "record revisions")
