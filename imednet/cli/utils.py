from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

import typer
from rich import print
from rich.table import Table

from ..config import load_config
from ..sdk import ImednetSDK

# Shared CLI argument for specifying a study key
STUDY_KEY_ARG = typer.Argument(..., help="The key identifying the study.")


def get_sdk() -> ImednetSDK:
    """Initialize and return the SDK instance using :func:`load_config`."""
    try:
        config = load_config()
    except ValueError:
        print(
            "[bold red]Error:[/bold red] IMEDNET_API_KEY and "
            "IMEDNET_SECURITY_KEY environment variables must be set."
        )
        raise typer.Exit(code=1)

    try:
        return ImednetSDK(
            api_key=config.api_key,
            security_key=config.security_key,
            base_url=config.base_url,
        )
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]Error initializing SDK:[/bold red] {exc}")
        raise typer.Exit(code=1)


def parse_filter_args(filter_args: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    """Parse a list of ``key=value`` strings into a dictionary."""
    if not filter_args:
        return None
    filter_dict: Dict[str, Union[str, bool, int]] = {}
    for arg in filter_args:
        if "=" not in arg:
            print(f"[bold red]Error:[/bold red] Invalid filter format: '{arg}'. Use 'key=value'.")
            raise typer.Exit(code=1)
        key, value = arg.split("=", 1)
        if value.lower() == "true":
            filter_dict[key.strip()] = True
        elif value.lower() == "false":
            filter_dict[key.strip()] = False
        elif value.isdigit():
            filter_dict[key.strip()] = int(value)
        else:
            filter_dict[key.strip()] = value
    return filter_dict


def echo_fetch(name: str, study_key: str | None = None) -> None:
    """Print a standardized fetching message."""
    msg = f"Fetching {name} for study '{study_key}'..." if study_key else f"Fetching {name}..."
    print(msg)


def _format_cell_value(value: Any) -> str:
    """Format a single cell value for display."""
    if value is None:
        return "[dim]-[/dim]"
    if isinstance(value, bool):
        return "[green]True[/green]" if value else "[dim]False[/dim]"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, (list, dict)):
        # Truncate very long list/dict representations
        s = str(value)
        return f"{s[:60]}..." if len(s) > 60 else s
    return str(value)


def display_list(items: Sequence[Any], label: str, empty_msg: str | None = None) -> None:
    """Print list output with a standardized format."""
    if not items:
        print(empty_msg or f"No {label} found.")
        return

    print(f"Found {len(items)} {label}:")

    # Try to determine if we can display this as a table
    first = items[0]
    data_list: List[Dict[str, Any]] = []

    if hasattr(first, "model_dump"):
        data_list = [item.model_dump() for item in items]
    elif hasattr(first, "dict"):
        data_list = [item.dict() for item in items]
    elif isinstance(first, dict):
        data_list = list(items)  # type: ignore

    if not data_list:
        print(items)
        return

    table = Table(show_header=True, header_style="bold magenta")
    headers = list(data_list[0].keys())

    for header in headers:
        table.add_column(str(header).replace("_", " ").title())

    for item in data_list:
        row = []
        for k in headers:
            val = item.get(k)
            row.append(_format_cell_value(val))
        table.add_row(*row)

    print(table)


def register_list_command(
    app: typer.Typer,
    attr: str,
    name: str,
    *,
    requires_study_key: bool = True,
    empty_msg: str | None = None,
) -> None:
    """Attach a standard ``list`` command to ``app``."""

    from .decorators import with_sdk  # imported lazily to avoid circular import

    if requires_study_key:

        @app.command("list")
        @with_sdk
        def list_cmd(sdk: ImednetSDK, study_key: str = STUDY_KEY_ARG) -> None:
            echo_fetch(name, study_key)
            items = getattr(sdk, attr).list(study_key)
            display_list(items, name, empty_msg)

        return

    else:

        @app.command("list")
        @with_sdk
        def list_cmd_no_study(sdk: ImednetSDK) -> None:
            echo_fetch(name)
            items = getattr(sdk, attr).list()
            display_list(items, name, empty_msg)

        return
