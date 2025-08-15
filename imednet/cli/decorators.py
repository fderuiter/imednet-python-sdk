from __future__ import annotations

import inspect
from functools import wraps
from typing import Callable, Concatenate, ParamSpec, TypeVar

import typer
from rich import print

from ..core.exceptions import ApiError
from ..sdk import ImednetSDK

P = ParamSpec("P")
R = TypeVar("R")


def with_sdk(func: Callable[Concatenate[ImednetSDK, P], R]) -> Callable[P, R]:
    """Initialize the SDK and pass it to the wrapped command function."""

    sig = inspect.signature(func)
    wrapper_params = list(sig.parameters.values())[1:]

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        from . import get_sdk  # local import so tests can monkeypatch

        sdk = get_sdk()
        try:
            return func(sdk, *args, **kwargs)
        except typer.Exit:  # allow commands to exit early
            raise
        except ApiError as exc:
            print(f"[bold red]API Error:[/bold red] {exc}")
            raise typer.Exit(code=1)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[bold red]Unexpected error:[/bold red] {exc}")
            raise typer.Exit(code=1)
        finally:
            close = getattr(sdk, "close", None)
            if callable(close):
                close()

    wrapper.__signature__ = sig.replace(parameters=wrapper_params)  # type: ignore[attr-defined]

    return wrapper
