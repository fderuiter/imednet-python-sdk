from __future__ import annotations

import typer

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, display_list, echo_fetch

app = typer.Typer(name="sites", help="Manage sites within a study.")


@app.command("list")
@with_sdk
def list_sites(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
) -> None:
    """List sites for a specific study."""
    echo_fetch("sites", study_key)
    sites_list = sdk.sites.list(study_key)
    display_list(sites_list, "sites", "No sites found for this study.")
