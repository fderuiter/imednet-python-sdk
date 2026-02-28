"""Asynchronous HTTP client for the iMednet API."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from imednet.core.http.executor import AsyncRequestExecutor
from imednet.core.retry import RetryPolicy

from .http_client_base import HTTPClientBase

logger = logging.getLogger(__name__)


class AsyncClient(HTTPClientBase[httpx.AsyncClient, AsyncRequestExecutor]):
    """Asynchronous variant of :class:`~imednet.core.client.Client`."""

    def _get_client_class(self) -> type[httpx.AsyncClient]:
        return httpx.AsyncClient

    def _create_executor(
        self, client: httpx.AsyncClient, retry_policy: Optional[RetryPolicy] = None
    ) -> AsyncRequestExecutor:

        # Use wrapper to allow mocking client.request after initialization
        async def send_wrapper(method: str, url: str, **kwargs: Any) -> httpx.Response:
            return await client.request(method, url, **kwargs)

        return AsyncRequestExecutor(
            send=send_wrapper,
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            tracer=self._tracer,
            retry_policy=retry_policy,
        )

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        return await self._executor(method, path, **kwargs)

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        return await self._request("GET", path, params=params, **kwargs)

    async def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        return await self._request("POST", path, json=json, **kwargs)
