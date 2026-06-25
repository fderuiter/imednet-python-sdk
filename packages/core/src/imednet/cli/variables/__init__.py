"""CLI commands for managing variables."""

from __future__ import annotations
import argparse

from ..utils import register_list_command

def setup_parser(subparsers):
    parser = subparsers.add_parser("variables", help="Manage variables.")
    register_list_command(
        parser,
        "variables",
        "variables",
        requires_study_key=True,
        summary_fields=["variable_name", "label", "variable_type", "form_name", "disabled"]
    )
