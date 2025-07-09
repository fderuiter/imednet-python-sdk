from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import typer
from rich import print

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


def display_list(items: Sequence[Any], label: str, empty_msg: str | None = None) -> None:
    """Print list output with a standardized format."""
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
