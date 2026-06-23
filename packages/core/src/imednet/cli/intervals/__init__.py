"""CLI commands for managing study intervals."""

from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="intervals", help="Manage intervals within a study.")

__all__ = ["app"]

register_list_command(
    app,
    "intervals",
    "intervals",
    summary_fields=["interval_id", "interval_name", "interval_sequence"],
)
