"""Asynchronous HTTP client for the iMednet API."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Dict, Optional, cast

import httpx

from .http_client_base import HTTPClientBase

logger = logging.getLogger(__name__)


class AsyncClient(HTTPClientBase):
    """Asynchronous variant of :class:`~imednet.core.client.Client`."""

    DEFAULT_BASE_URL = HTTPClientBase.DEFAULT_BASE_URL

    HTTPX_CLIENT_CLS = httpx.AsyncClient
    IS_ASYNC = True

    async def __aenter__(self) -> "AsyncClient":
        """Enter the async context manager.

        Returns:
            The async client instance.
        """
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Exit the async context manager and close the client.

        Args:
            exc_type: The exception type.
            exc: The exception instance.
            tb: The traceback.
        """
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async GET request.

        Args:
            path: URL path or full URL.
            params: Query parameters.
            **kwargs: Additional keyword arguments to pass to the HTTP client.

        Returns:
            The HTTP response.

        Raises:
            APIError: If the API returns an error.
        """
        return await cast(
            Awaitable[httpx.Response],
            self._request("GET", path, params=params, **kwargs),
        )

    async def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async POST request.

        Args:
            path: URL path or full URL.
            json: JSON body for the request.
            **kwargs: Additional keyword arguments to pass to the HTTP client.

        Returns:
            The HTTP response.

        Raises:
            APIError: If the API returns an error.
        """
        return await cast(
            Awaitable[httpx.Response],
            self._request("POST", path, json=json, **kwargs),
        )
