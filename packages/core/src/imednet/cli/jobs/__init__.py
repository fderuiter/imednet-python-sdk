"""CLI commands for monitoring background jobs."""

from __future__ import annotations

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, fetching_status


def setup_parser(subparsers):
    """Setup the parser for this module."""
    parser = subparsers.add_parser("jobs", help="Manage background jobs.")
    sub = parser.add_subparsers(dest="command")

    status_parser = sub.add_parser("status", help="Fetch a job's current status.")
    status_parser.add_argument("study_key", help=STUDY_KEY_ARG)
    status_parser.add_argument("batch_id", help="Job batch ID.")

    @with_sdk
    def job_status(sdk: ImednetSDK, study_key: str, batch_id: str) -> None:
        with fetching_status("job status", study_key):
            job = sdk.get_job(study_key, batch_id)
        print(job.model_dump())

    status_parser.set_defaults(
        func=lambda args: job_status(study_key=args.study_key, batch_id=args.batch_id)
    )

    wait_parser = sub.add_parser("wait", help="Wait for a job to reach a terminal state.")
    wait_parser.add_argument("study_key", help=STUDY_KEY_ARG)
    wait_parser.add_argument("batch_id", help="Job batch ID.")
    wait_parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds.")
    wait_parser.add_argument("--timeout", type=int, default=300, help="Maximum time to wait.")

    @with_sdk
    def job_wait(
        sdk: ImednetSDK, study_key: str, batch_id: str, interval: int, timeout: int
    ) -> None:
        with fetching_status("job result", study_key):
            job = sdk.poll_job(study_key, batch_id, interval=interval, timeout=timeout)
        print(job.model_dump())

    wait_parser.set_defaults(
        func=lambda args: job_wait(
            study_key=args.study_key,
            batch_id=args.batch_id,
            interval=args.interval,
            timeout=args.timeout,
        )
    )
