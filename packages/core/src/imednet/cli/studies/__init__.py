"""CLI commands for managing studies."""

from __future__ import annotations
import argparse

from ..utils import register_list_command

def setup_parser(subparsers):
    parser = subparsers.add_parser("studies", help="Manage studies.")
    register_list_command(
        parser,
        "studies",
        "studies",
        requires_study_key=False,
        summary_fields=["study_key", "study_name", "study_type", "sponsor_key"],
    )
