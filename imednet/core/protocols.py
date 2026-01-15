"""
Protocols for core components to decouple implementation from usage.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, runtime_checkable

import httpx


@runtime_checkable
class ResourceClient(Protocol):
    """Protocol for a synchronous HTTP client."""

    base_url: str

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response: ...

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response: ...


@runtime_checkable
class AsyncResourceClient(Protocol):
    """Protocol for an asynchronous HTTP client."""

    base_url: str

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response: ...

    async def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response: ...
