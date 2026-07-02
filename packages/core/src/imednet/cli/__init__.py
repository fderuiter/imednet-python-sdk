"""iMednet Command Line Interface."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from importlib import import_module
from importlib.util import find_spec
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:

    def load_dotenv(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        pass

    print(
        "Warning: python-dotenv not installed. Install with `pip install 'imednet[cli]'` to load .env files automatically.",
        file=sys.stderr,
    )

from ..integrations import SinkConfig  # noqa: F401
from ..integrations.export import (
    export_to_csv,
    export_to_duckdb,
    export_to_excel,
    export_to_json,
    export_to_long_sql,
    export_to_parquet,
    export_to_sql,
    export_to_sql_by_form,
)
from .decorators import with_sdk
from .utils import get_sdk, parse_filter_args

__all__ = [
    "app",
    "get_parser",
    "with_sdk",
    "get_sdk",
    "parse_filter_args",
    "export_to_csv",
    "export_to_duckdb",
    "export_to_excel",
    "export_to_json",
    "export_to_long_sql",
    "export_to_parquet",
    "export_to_sql",
    "export_to_sql_by_form",
    "SinkConfig",
]


def _setup_standalone_scripts(subparsers):
    import glob

    script_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "scripts")
    for script_path in glob.glob(os.path.join(script_dir, "*.py")):
        name = os.path.basename(script_path)[:-3]
        if name == "__init__":
            continue

        # We need a dash format for command names
        cmd_name = name.replace("_", "-")
        parser = subparsers.add_parser(cmd_name, help=f"Run {name} script.")
        parser.add_argument(
            "args", nargs=argparse.REMAINDER, help="Arguments passed to the script."
        )

        def run_script(args, script_path=script_path):
            import subprocess

            res = subprocess.run([sys.executable, script_path] + args.args)
            if res.returncode != 0:
                sys.exit(res.returncode)

        parser.set_defaults(func=run_script)


def get_parser() -> argparse.ArgumentParser:
    """Return the main argparse.ArgumentParser for the CLI."""
    parser = argparse.ArgumentParser(description="iMednet SDK Command Line Interface")
    parser.add_argument(
        "--high-contrast", action="store_true", help="Enable high-contrast mode for accessibility."
    )

    subparsers = parser.add_subparsers(dest="command")

    from .export import setup_parser as export_setup
    from .intervals import setup_parser as intervals_setup
    from .jobs import setup_parser as jobs_setup
    from .queries import setup_parser as queries_setup
    from .record_revisions import setup_parser as record_revisions_setup
    from .records import setup_parser as records_setup
    from .sites import setup_parser as sites_setup
    from .studies import setup_parser as studies_setup
    from .subjects import setup_parser as subjects_setup
    from .variables import setup_parser as variables_setup

    studies_setup(subparsers)
    queries_setup(subparsers)
    variables_setup(subparsers)
    record_revisions_setup(subparsers)
    sites_setup(subparsers)
    export_setup(subparsers)
    subjects_setup(subparsers)
    intervals_setup(subparsers)
    jobs_setup(subparsers)
    records_setup(subparsers)
    _setup_standalone_scripts(subparsers)

    import importlib.metadata
    
    # Discover and register CLI plugins using entry points
    for entry_point in importlib.metadata.entry_points(group="imednet.cli_plugins"):
        try:
            plugin_setup = entry_point.load()
            plugin_setup(subparsers)
        except Exception as e:
            print(f"Warning: Failed to load CLI plugin '{entry_point.name}': {e}", file=sys.stderr)

    return parser


def app(args=None):
    """Main entrypoint for the CLI."""
    if args is None:
        args = sys.argv[1:]

    parser = get_parser()

    parsed = parser.parse_args(args)

    if parsed.high_contrast:
        os.environ["IMEDNET_HIGH_CONTRAST"] = "1"

    if hasattr(parsed, "func"):
        parsed.func(parsed)
    else:
        parser.print_help()


if __name__ == "__main__":
    app()
