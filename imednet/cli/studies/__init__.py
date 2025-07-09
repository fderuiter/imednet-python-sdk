from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="studies", help="Manage studies.")

register_list_command(app, "studies", "studies", requires_study_key=False)
