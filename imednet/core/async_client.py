"""Asynchronous HTTP client for the iMednet API."""

from __future__ import annotations

import logging
import time
from contextlib import nullcontext
from typing import Any, Dict, Optional, Union

try:  # optional opentelemetry
    from opentelemetry import trace
    from opentelemetry.trace import Tracer
except Exception:  # pragma: no cover - optional dependency
    trace = None
    Tracer = None
import httpx
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_exponential

from .base_client import BaseClient
from .exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class AsyncClient(BaseClient):
    """Asynchronous HTTP client derived from :class:`~imednet.core.base_client.BaseClient`."""

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

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._should_retry,
            reraise=True,
        )

        span_cm = (
            self._tracer.start_as_current_span(
                "http_request", attributes={"endpoint": url, "method": method}
            )
            if self._tracer
            else nullcontext()
        )

        async with span_cm as span:
            try:
                start = time.monotonic()
                async for attempt in retryer:
                    with attempt:
                        response = await self._client.request(method, url, **kwargs)
                latency = time.monotonic() - start
                logger.info(
                    "http_request",
                    extra={
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "latency": latency,
                    },
                )
            except RetryError as e:
                logger.error("Request failed after retries: %s", e)
                raise RequestError("Network request failed after retries")

            if span is not None:
                span.set_attribute("status_code", response.status_code)

        if response.is_error:
            status = response.status_code
            try:
                body = response.json()
            except Exception:
                body = response.text
            if status == 400:
                raise ValidationError(body)
            if status == 401:
                raise AuthenticationError(body)
            if status == 403:
                raise AuthorizationError(body)
            if status == 404:
                raise NotFoundError(body)
            if status == 429:
                raise RateLimitError(body)
            if 500 <= status < 600:
                raise ServerError(body)
            raise ApiError(body)

        return response

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
