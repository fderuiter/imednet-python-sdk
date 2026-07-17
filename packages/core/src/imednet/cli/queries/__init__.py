"""CLI commands for managing queries."""

from __future__ import annotations

from ..utils import register_list_command


def setup_parser(subparsers):
    """Setup the parser for this module."""
    parser = subparsers.add_parser("queries", help="Manage queries.")
    register_list_command(
        parser,
        "queries",
        "queries",
        requires_study_key=True,
        summary_fields=[
            "description",
            "annotation_type",
            "subject_key",
            "variable",
            "date_created",
        ],
    )
