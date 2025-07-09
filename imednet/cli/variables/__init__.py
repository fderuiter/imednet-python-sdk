from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="variables", help="Manage variables within a study.")

register_list_command(app, "variables", "variables")
