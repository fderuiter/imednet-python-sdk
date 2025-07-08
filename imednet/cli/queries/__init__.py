from __future__ import annotations

import typer

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, display_list, echo_fetch

app = typer.Typer(name="queries", help="Manage queries within a study.")


@app.command("list")
@with_sdk
def list_queries(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
) -> None:
    """List queries for a study."""
    echo_fetch("queries", study_key)
    queries = sdk.queries.list(study_key)
    display_list(queries, "queries")
