"""Asynchronous entry point for the iMednet SDK."""

from __future__ import annotations

from typing import Any

from .sdk import ImednetSDK


class AsyncImednetSDK(ImednetSDK):
    """Async variant of :class:`ImednetSDK` using the async HTTP client."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - thin wrapper
        kwargs["enable_async"] = True
        super().__init__(*args, **kwargs)

    async def __aenter__(self) -> "AsyncImednetSDK":
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
