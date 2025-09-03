from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import typer
from rich import print

from ..sdk import ImednetSDK

# Shared CLI argument for specifying a study key
STUDY_KEY_ARG = typer.Argument(..., help="The key identifying the study.")


def parse_filter_args(filter_args: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    """Parse a list of `key=value` strings into a dictionary for filtering.

    This function supports boolean and integer conversion for values.

    Args:
        filter_args: A list of strings, each in `key=value` format.

    Returns:
        A dictionary of parsed filters, or `None` if the input is empty.

    Raises:
        typer.Exit: If a filter string is not in the correct format.
    """
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
    """Print a standardized message to the console indicating data is being fetched.

    Args:
        name: The name of the resource being fetched (e.g., "studies", "records").
        study_key: An optional study key to include in the message.
    """
    msg = f"Fetching {name} for study '{study_key}'..." if study_key else f"Fetching {name}..."
    print(msg)


def display_list(items: Sequence[Any], label: str, empty_msg: str | None = None) -> None:
    """Display a list of items to the console in a standardized format.

    Args:
        items: A sequence of items to display.
        label: A label for the items being displayed (e.g., "studies", "records").
        empty_msg: An optional message to display if the list is empty.
    """
    if items:
        print(f"Found {len(items)} {label}:")
        print(items)
    else:
        print(empty_msg or f"No {label} found.")


def register_list_command(
    app: typer.Typer,
    attr: str,
    name: str,
    *,
    requires_study_key: bool = True,
    empty_msg: str | None = None,
) -> None:
    """Register a standard `list` command with a Typer application.

    This helper function creates a `list` command that fetches and displays a
    list of resources from the SDK.

    Args:
        app: The Typer application to add the command to.
        attr: The attribute name of the SDK endpoint to call (e.g., "studies").
        name: The name of the resource being listed (e.g., "studies").
        requires_study_key: If `True`, the command will require a `study_key` argument.
        empty_msg: An optional message to display if no items are found.
    """
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
