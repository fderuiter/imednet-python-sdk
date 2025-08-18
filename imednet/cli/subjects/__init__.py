from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="subjects", help="Manage subjects within a study.")

register_list_command(
    app,
    "subjects",
    "subjects",
    with_filter=True,
    filter_help_example="subject_status=Screened",
    empty_msg="No subjects found matching the criteria.",
)
