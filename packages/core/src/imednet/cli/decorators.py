"""TODO: Add docstring."""

from __future__ import annotations

import inspect
import os
from functools import wraps
from typing import Callable, Concatenate, ParamSpec, TypeVar

import typer
from rich import print
from rich.markup import escape

from imednet.errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
)

from ..sdk import ImednetSDK

P = ParamSpec("P")
R = TypeVar("R")


def _redact_secrets(msg: str) -> str:
    """Redact secrets from error messages."""
    for env_var in ["IMEDNET_API_KEY", "IMEDNET_SECURITY_KEY"]:
        val = os.environ.get(env_var)
        if val and val in msg:
            msg = msg.replace(val, "********")
    return msg


def with_sdk(func: Callable[Concatenate[ImednetSDK, P], R]) -> Callable[P, R]:
    """Initialize the SDK and pass it to the wrapped command function."""
    sig = inspect.signature(func)
    wrapper_params = list(sig.parameters.values())[1:]

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """TODO: Add docstring."""
        from .utils.context import get_sdk

        sdk = get_sdk()
        try:
            return func(sdk, *args, **kwargs)
        except typer.Exit:  # allow commands to exit early
            raise
        except (AuthenticationError, UnauthorizedError) as exc:
            msg = _redact_secrets(str(exc))
            print(f"[bold red]Authentication Failed:[/bold red] {escape(msg)}")
            raise typer.Exit(code=1)
        except (AuthorizationError, ForbiddenError) as exc:
            msg = _redact_secrets(str(exc))
            print(f"[bold red]Permission Denied:[/bold red] {escape(msg)}")
            raise typer.Exit(code=1)
        except RateLimitError as exc:
            msg = _redact_secrets(str(exc))
            print(f"[bold red]Rate Limit Exceeded:[/bold red] {escape(msg)}")
            raise typer.Exit(code=1)
        except NotFoundError as exc:
            msg = _redact_secrets(str(exc))
            print(f"[bold red]Not Found:[/bold red] {escape(msg)}")
            raise typer.Exit(code=1)
        except ApiError as exc:
            msg = _redact_secrets(str(exc))
            print(f"[bold red]API Error:[/bold red] {escape(msg)}")
            raise typer.Exit(code=1)
        except KeyboardInterrupt:
            print("\n[bold yellow]Aborted by user.[/bold yellow]")
            raise typer.Exit(code=130)
        except Exception as exc:  # pragma: no cover - defensive
            msg = _redact_secrets(str(exc))
            print(f"[bold red]Unexpected error:[/bold red] {escape(msg)}")
            raise typer.Exit(code=1)
        finally:
            close = getattr(sdk, "close", None)
            if callable(close):
                close()

    wrapper.__signature__ = sig.replace(parameters=wrapper_params)  # type: ignore[attr-defined]

    return wrapper
