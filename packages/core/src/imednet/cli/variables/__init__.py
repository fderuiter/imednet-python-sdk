"""TODO: Add docstring."""
from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="variables", help="Manage variables within a study.")

__all__ = ["app"]

register_list_command(
    app,
    "variables",
    "variables",
    summary_fields=["variable_name", "label", "variable_type", "form_name", "disabled"],
)
