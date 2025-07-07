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
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
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
        return await cast(
            Awaitable[httpx.Response],
            self._request("POST", path, json=json, **kwargs),
        )
