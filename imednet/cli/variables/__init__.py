from __future__ import annotations

import typer

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, display_list, echo_fetch

app = typer.Typer(name="variables", help="Manage variables within a study.")


@app.command("list")
@with_sdk
def list_variables(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
) -> None:
    """List variables for a study."""
    echo_fetch("variables", study_key)
    variables = sdk.variables.list(study_key)
    display_list(variables, "variables")
