"""CLI commands for managing study subjects."""

from __future__ import annotations

import argparse

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, display_list, fetching_status, parse_filter_args


def setup_parser(subparsers):
    """Setup the parser for this module."""
    parser = subparsers.add_parser("subjects", help="Manage subjects within a study.")
    sub = parser.add_subparsers(dest="command")
    list_parser = sub.add_parser("list", help="List subjects for a specific study.")
    list_parser.add_argument("study_key", help=STUDY_KEY_ARG)
    list_parser.add_argument(
        "-f",
        "--filter",
        action="append",
        dest="subject_filter",
        help="Filter criteria (e.g., 'subject_status=Screened'). Repeat for multiple filters.",
    )

    @with_sdk
    def list_subjects(
        sdk: ImednetSDK, study_key: str, subject_filter: list[str] | None = None
    ) -> None:
        parsed_filter = parse_filter_args(subject_filter)

        with fetching_status("subjects", study_key):
            subjects_list = sdk.subjects.list(study_key, **(parsed_filter or {}))

        view_models = []
        for s in subjects_list:
            keywords_str = ", ".join(k.keyword_name for k in s.keywords)
            view_models.append(
                {
                    "subject_key": s.subject_key,
                    "status": s.subject_status,
                    "site": s.site_name,
                    "enrollment_date": s.enrollment_start_date,
                    "keywords": keywords_str,
                }
            )

        display_list(view_models, "subjects", "No subjects found matching the criteria.")

    list_parser.set_defaults(
        func=lambda args: list_subjects(
            study_key=args.study_key, subject_filter=args.subject_filter
        )
    )
