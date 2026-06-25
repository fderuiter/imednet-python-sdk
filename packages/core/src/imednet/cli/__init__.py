"""iMednet Command Line Interface."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from importlib import import_module
from importlib.util import find_spec

from dotenv import load_dotenv

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

load_dotenv()


def run_dashboard(port: int = 8501, no_browser: bool = False) -> None:
    """Launch the interactive iMednet Streamlit reporting dashboard."""
    streamlit_spec = find_spec("imednet_streamlit")
    if streamlit_spec is None:
        print("Dashboard plugin not found. Install it with:\n  pip install imednet-streamlit")
        sys.exit(1)

    dashboard_spec = find_spec("imednet_streamlit.app")
    if dashboard_spec is None:
        print("Dashboard plugin not found. Install it with:\n  pip install imednet-streamlit")
        sys.exit(1)

    app_path = dashboard_spec.origin
    if app_path is None:
        print("Cannot resolve dashboard app path.")
        sys.exit(1)

    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.port", str(port)]
    if no_browser:
        cmd += ["--server.headless", "true"]

    print(f"Launching iMednet Dashboard on port {port}...")
    try:
        result = subprocess.run(cmd, check=False)
    except OSError as exc:
        print(f"Dashboard failed to launch: {exc}")
        sys.exit(1)

    if result.returncode != 0:
        print("Dashboard failed to launch.")
        sys.exit(result.returncode)


def _exit_missing_plugin(name: str) -> None:
    print(f"The {name} plugin is not installed.")
    sys.exit(1)


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


def app(args=None):
    """Main entrypoint for the CLI."""
    if args is None:
        args = sys.argv[1:]

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

    # dashboard
    dash_parser = subparsers.add_parser(
        "dashboard", help="Launch the iMednet Streamlit reporting dashboard."
    )
    dash_parser.add_argument(
        "-p", "--port", type=int, default=8501, help="Port to run the dashboard on."
    )
    dash_parser.add_argument(
        "--no-browser", action="store_true", help="Suppress automatic browser launch."
    )
    dash_parser.set_defaults(func=lambda a: run_dashboard(port=a.port, no_browser=a.no_browser))

    # workflows
    try:
        from imednet_workflows.cli import setup_parser as wf_setup
        from imednet_workflows.cli import setup_subject_parser as subj_setup

        wf_setup(subparsers)
        subj_setup(subparsers)
    except ImportError:
        # Fallbacks when plugin not installed
        wf_parser = subparsers.add_parser(
            "workflows", help="Execute opinionated business logic (requires imednet-workflows)."
        )
        wf_sub = wf_parser.add_subparsers(dest="wf_command")

        extract_parser = wf_sub.add_parser("extract-records")
        extract_parser.set_defaults(func=lambda a: _exit_missing_plugin("workflows"))

        subj_parser = subparsers.add_parser(
            "subject-data", help="Retrieve all data for a single subject."
        )
        subj_parser.set_defaults(func=lambda a: _exit_missing_plugin("workflows"))

        sync_parser = wf_sub.add_parser(
            "sync-worker", help="Run a background cache synchronization worker."
        )
        sync_parser.set_defaults(func=lambda a: _exit_missing_plugin("workflows"))

    # allow intercept workflows if imednet_workflows is installed and changes this
    # Wait, imednet_workflows tries to do `app.add_typer(...)`. We need to provide a mock add_typer for backwards compat.

    parsed = parser.parse_args(args)

    if parsed.high_contrast:
        os.environ["IMEDNET_HIGH_CONTRAST"] = "1"

    if hasattr(parsed, "func"):
        parsed.func(parsed)
    else:
        parser.print_help()


# We need to provide dummy methods on `app` for imednet_workflows so it doesn't crash when it imports `app`
def _dummy_add_typer(*args, **kwargs):
    pass


def _dummy_command(*args, **kwargs):
    def wrapper(f):
        return f

    return wrapper


def _dummy_callback(*args, **kwargs):
    def wrapper(f):
        return f

    return wrapper


app.add_typer = _dummy_add_typer  # type: ignore[attr-defined]
app.command = _dummy_command  # type: ignore[attr-defined]
app.callback = _dummy_callback  # type: ignore[attr-defined]

if __name__ == "__main__":
    app()
