"""
Core protocols for the iMednet SDK.

These protocols define the interfaces for core components, enabling dependency inversion
and easier testing.
"""

from typing import Any, Dict, Optional, Protocol, runtime_checkable

import httpx


@runtime_checkable
class RequestorProtocol(Protocol):
    """Protocol for a synchronous HTTP requestor."""

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
    """Protocol for an asynchronous HTTP requestor."""

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a GET request asynchronously."""
        ...

    async def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a POST request asynchronously."""
        ...
