from __future__ import annotations

import typer

from ..utils import register_list_command

app = typer.Typer(name="queries", help="Manage queries within a study.")

register_list_command(
    app,
    "queries",
    "queries",
    summary_fields=[
        "description",
        "annotation_type",
        "subject_key",
        "variable",
        "date_created",
    ],
)
