from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Sequence

from rich import print
from rich.console import Console
from rich.markup import escape
from rich.table import Table

# Map status strings to Rich colors for O(1) lookup
_STATUS_COLOR_MAP = {
    # Green (Success/Active)
    "active": "green",
    "success": "green",
    "ok": "green",
    "completed": "green",
    "open": "green",
    "approved": "green",
    "verified": "green",
    # Yellow (Pending/Processing)
    "pending": "yellow",
    "processing": "yellow",
    "suspended": "yellow",
    "hold": "yellow",
    "incomplete": "yellow",
    "initiated": "yellow",
    # Red (Failure/Inactive)
    "inactive": "red",
    "closed": "red",
    "error": "red",
    "fail": "red",
    "failed": "red",
    "rejected": "red",
    "terminated": "red",
    "withdrawn": "red",
}

console = Console()


def _truncate(text: str, length: int = 60) -> str:
    """Truncate text to a maximum length with ellipsis."""
    return f"{text[:length]}..." if len(text) > length else text


def _format_cell_value(value: Any, key: str | None = None) -> str:
    """Format a single cell value for display."""
    if value is None:
        return "[dim]-[/dim]"
    if isinstance(value, bool):
        return "[green]Yes[/green]" if value else "[dim]No[/dim]"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")

    str_val = str(value)

    # Colorize status columns
    if key and any(k in key.lower() for k in ("status", "state")):
        lower_val = str_val.lower()
        if color := _STATUS_COLOR_MAP.get(lower_val):
            return f"[{color}]{escape(str_val)}[/{color}]"

    if isinstance(value, list) and all(isinstance(x, (str, int, float, bool)) for x in value):
        if not value:
            return "[dim]-[/dim]"
        s = ", ".join(str(x) for x in value)
        return escape(_truncate(s))
    if isinstance(value, (list, dict)):
        # Truncate very long list/dict representations
        return escape(_truncate(str(value)))
    return escape(str_val)


def _create_table(items: Sequence[Any], fields: List[str]) -> Table:
    """Create a Rich table from a list of items and specified fields."""
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
            row.append(_format_cell_value(val, key=str(k)))
        table.add_row(*row)
    return table


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
        table = _create_table(items, fields)
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

    all_keys = list(data_list[0].keys())
    table = _create_table(data_list, all_keys)
    print(table)
