from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

import typer
from rich import print
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from ..config import load_config
from ..sdk import ImednetSDK

# Shared CLI argument for specifying a study key
STUDY_KEY_ARG = typer.Argument(..., help="The key identifying the study.")

console = Console()


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
        print(f"[bold red]Error initializing SDK:[/bold red] {escape(str(exc))}")
        raise typer.Exit(code=1)


def parse_filter_args(filter_args: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    """Parse a list of ``key=value`` strings into a dictionary."""
    if not filter_args:
        return None
    filter_dict: Dict[str, Union[str, bool, int]] = {}
    for arg in filter_args:
        if "=" not in arg:
            print(
                f"[bold red]Error:[/bold red] Invalid filter format: '{escape(arg)}'. "
                "Use 'key=value'."
            )
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


@contextmanager
def fetching_status(name: str, study_key: str | None = None):
    """Context manager to show a spinner while fetching data."""
    if study_key:
        msg = f"Fetching {escape(name)} for study '{escape(study_key)}'..."
    else:
        msg = f"Fetching {escape(name)}..."
    with console.status(f"[bold blue]{msg}[/bold blue]", spinner="dots"):
        yield


def _truncate(text: str, length: int = 60) -> str:
    """Truncate text to a maximum length with ellipsis."""
    return f"{text[:length]}..." if len(text) > length else text


def _format_cell_value(value: Any) -> str:
    """Format a single cell value for display."""
    if value is None:
        return "[dim]-[/dim]"
    if isinstance(value, bool):
        return "[green]Yes[/green]" if value else "[dim]No[/dim]"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, list) and all(isinstance(x, (str, int, float, bool)) for x in value):
        if not value:
            return "[dim]-[/dim]"
        s = ", ".join(str(x) for x in value)
        return escape(_truncate(s))
    if isinstance(value, (list, dict)):
        # Truncate very long list/dict representations
        return escape(_truncate(str(value)))
    return escape(str(value))


def display_list(
    items: Sequence[Any],
    label: str,
    empty_msg: str | None = None,
    fields: List[str] | None = None,
) -> None:
    """Print list output with a standardized format."""
    if not items:
        print(empty_msg or f"No {label} found.")
        return

    print(f"Found {len(items)} {label}:")

    # Bolt Optimization: If specific fields are requested, extract them directly
    # from the objects instead of converting everything to a dictionary.
    # This avoids O(N*M) overhead for large lists where M is total field count.
    if fields:
        table = Table(show_header=True, header_style="bold magenta")
        for header in fields:
            table.add_column(str(header).replace("_", " ").title())

        for item in items:
            row = []
            for k in fields:
                if isinstance(item, dict):
                    val = item.get(k)
                else:
                    # Use getattr for Pydantic models or objects
                    val = getattr(item, k, None)
                row.append(_format_cell_value(val))
            table.add_row(*row)

        print(table)
        return

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
    all_keys = list(data_list[0].keys())
    headers = all_keys

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
    summary_fields: List[str] | None = None,
) -> None:
    """Attach a standard ``list`` command to ``app``."""

    from .decorators import with_sdk  # imported lazily to avoid circular import

    if requires_study_key:

        @app.command("list")
        @with_sdk
        def list_cmd(sdk: ImednetSDK, study_key: str = STUDY_KEY_ARG) -> None:
            with fetching_status(name, study_key):
                items = getattr(sdk, attr).list(study_key)
            display_list(items, name, empty_msg, fields=summary_fields)

        return

    else:

        @app.command("list")
        @with_sdk
        def list_cmd_no_study(sdk: ImednetSDK) -> None:
            with fetching_status(name):
                items = getattr(sdk, attr).list()
            display_list(items, name, empty_msg, fields=summary_fields)

        return
