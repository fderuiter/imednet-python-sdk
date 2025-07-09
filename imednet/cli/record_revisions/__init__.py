from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="record-revisions", help="Manage record revision history.")

register_list_command(app, "record_revisions", "record revisions")
