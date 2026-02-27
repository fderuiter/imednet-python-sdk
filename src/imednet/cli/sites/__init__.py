from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="sites", help="Manage sites within a study.")

register_list_command(
    app,
    "sites",
    "sites",
    empty_msg="No sites found for this study.",
    summary_fields=["site_id", "site_name", "site_enrollment_status"],
)
