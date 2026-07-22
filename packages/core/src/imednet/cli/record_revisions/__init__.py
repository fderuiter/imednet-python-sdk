"""CLI commands for managing record revisions."""

from __future__ import annotations

import argparse
from typing import Any

from ..utils import register_list_command


def setup_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Setup the parser for this module."""
    parser = subparsers.add_parser("record-revisions", help="Manage record revisions.")
    register_list_command(
        parser,
        "record_revisions",
        "record revisions",
        requires_study_key=True,
    )
