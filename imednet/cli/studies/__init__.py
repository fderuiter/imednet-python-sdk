from __future__ import annotations

import typer

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import display_list, echo_fetch

app = typer.Typer(name="studies", help="Manage studies.")


@app.command("list")
@with_sdk
def list_studies(sdk: ImednetSDK) -> None:
    """List available studies."""
    echo_fetch("studies")
    studies_list = sdk.studies.list()
    display_list(studies_list, "studies")
