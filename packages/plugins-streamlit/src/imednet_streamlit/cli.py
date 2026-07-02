"""CLI commands for iMednet Streamlit dashboard."""

import subprocess
import sys
from importlib.util import find_spec


def run_dashboard(port: int = 8501, no_browser: bool = False) -> None:
    """Launch the interactive iMednet Streamlit reporting dashboard."""
    dashboard_spec = find_spec("imednet_streamlit.app")
    if dashboard_spec is None:
        print(
            "Dashboard app not found. Please ensure it is installed via `pip install imednet-streamlit`."
        )
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


def setup_parser(subparsers):
    """Set up the dashboard argparse subparsers."""
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
