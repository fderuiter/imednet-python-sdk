from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

import typer
from rich import print

from ..sdk import ImednetSDK


def get_sdk() -> ImednetSDK:
    """Initialize and return the SDK instance using environment variables."""
    api_key = os.getenv("IMEDNET_API_KEY")
    security_key = os.getenv("IMEDNET_SECURITY_KEY")
    base_url = os.getenv("IMEDNET_BASE_URL")

    if not api_key or not security_key:
        print(
            "[bold red]Error:[/bold red] IMEDNET_API_KEY and "
            "IMEDNET_SECURITY_KEY environment variables must be set."
        )
        raise typer.Exit(code=1)

    try:
        return ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url or None)
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
