"""CLI commands for managing record revisions."""

from __future__ import annotations
import argparse

from ..utils import register_list_command

def setup_parser(subparsers):
    parser = subparsers.add_parser("record-revisions", help="Manage record revisions.")
    register_list_command(
        parser,
        "record_revisions",
        "record revisions",
        requires_study_key=True,
        
    )
