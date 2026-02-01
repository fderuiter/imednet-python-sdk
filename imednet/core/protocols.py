"""Core protocols for dependency inversion."""

from typing import Any, Awaitable, Dict, Optional, Protocol, runtime_checkable

import httpx


@runtime_checkable
class RequestorProtocol(Protocol):
    """Protocol for synchronous HTTP clients."""

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a GET request."""
        ...

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a POST request."""
        ...


@runtime_checkable
class AsyncRequestorProtocol(Protocol):
    """Protocol for asynchronous HTTP clients."""

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Awaitable[httpx.Response]:
        """Make a GET request."""
        ...

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Awaitable[httpx.Response]:
        """Make a POST request."""
        ...
