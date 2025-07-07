"""Asynchronous HTTP client for the iMednet API."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Dict, Optional, Union, cast

import httpx

from ._requester import RequestExecutor
from .base_client import BaseClient, Tracer

logger = logging.getLogger(__name__)


class AsyncClient(BaseClient):
    """Asynchronous variant of :class:`~imednet.core.client.Client`."""

    DEFAULT_BASE_URL = BaseClient.DEFAULT_BASE_URL

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout] = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        log_level: Union[int, str] = logging.INFO,
        tracer: Optional[Tracer] = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            log_level=log_level,
            tracer=tracer,
        )
        self._executor = RequestExecutor(
            lambda *a, **kw: self._client.request(*a, **kw),
            is_async=True,
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            tracer=self._tracer,
        )

    def _create_client(self, api_key: str, security_key: str) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "x-imn-security-key": security_key,
            },
            timeout=self.timeout,
        )

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
            self._executor("GET", path, params=params, **kwargs),
        )

    async def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        return await cast(
            Awaitable[httpx.Response],
            self._executor("POST", path, json=json, **kwargs),
        )
