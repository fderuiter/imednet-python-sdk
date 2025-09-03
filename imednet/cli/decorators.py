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
    """A decorator that creates an `ImednetSDK` instance and passes it to the command.

    This decorator also handles common exceptions, such as `ApiError` and
    `ValueError`, printing a formatted error message and exiting with a non-zero
    status code. It ensures that the SDK's `close` method is called after the
    command has finished.

    Args:
        func: The command function to wrap. It must accept an `ImednetSDK`
            instance as its first argument.

    Returns:
        The wrapped command function.
    """
    sig = inspect.signature(func)
    wrapper_params = list(sig.parameters.values())[1:]

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            sdk = ImednetSDK()
            return func(sdk, *args, **kwargs)
        except typer.Exit:  # allow commands to exit early
            raise
        except ValueError as exc:
            print(f"[bold red]Error:[/bold red] {exc}")
            raise typer.Exit(code=1)
        except ApiError as exc:
            print(f"[bold red]API Error:[/bold red] {exc}")
            raise typer.Exit(code=1)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[bold red]Unexpected error:[/bold red] {exc}")
            raise typer.Exit(code=1)
        finally:
            if "sdk" in locals():
                close = getattr(sdk, "close", None)
                if callable(close):
                    close()

    wrapper.__signature__ = sig.replace(parameters=wrapper_params)  # type: ignore[attr-defined]

    return wrapper
