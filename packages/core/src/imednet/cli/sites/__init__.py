"""CLI commands for managing sites."""

from __future__ import annotations

import argparse

from ..utils import register_list_command


def setup_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Setup the parser for this module."""
    parser = subparsers.add_parser("sites", help="Manage sites.")
    register_list_command(
        parser,
        "sites",
        "sites",
        requires_study_key=True,
        empty_msg="No sites found for this study.",
        summary_fields=["site_id", "site_name", "site_enrollment_status"],
    )
