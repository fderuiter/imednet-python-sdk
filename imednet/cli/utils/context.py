from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import typer
from rich import print
from rich.markup import escape

from imednet.config import load_config
from imednet.sdk import ImednetSDK

from .output import console


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


@contextmanager
def fetching_status(name: str, study_key: str | None = None) -> Iterator[None]:
    """Context manager to show a spinner while fetching data."""
    if study_key:
        msg = f"Fetching {escape(name)} for study '{escape(study_key)}'..."
    else:
        msg = f"Fetching {escape(name)}..."
    with console.status(f"[bold blue]{msg}[/bold blue]", spinner="dots"):
        yield
