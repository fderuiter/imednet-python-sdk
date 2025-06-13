"""Asynchronous HTTP client for the iMednet API."""

from __future__ import annotations

import logging
import os
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
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    stop_after_attempt,
    wait_exponential,
)

from imednet.utils import sanitize_base_url
from imednet.utils.json_logging import configure_json_logging

from .client import Client
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


class AsyncClient:
    """Asynchronous variant of :class:`~imednet.core.client.Client`."""

    DEFAULT_BASE_URL = Client.DEFAULT_BASE_URL

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
        api_key = (api_key or os.getenv("IMEDNET_API_KEY") or "").strip()
        security_key = (security_key or os.getenv("IMEDNET_SECURITY_KEY") or "").strip()
        if not api_key or not security_key:
            raise ValueError("API key and security key are required")

        raw_base_url = base_url or os.getenv("IMEDNET_BASE_URL") or self.DEFAULT_BASE_URL
        self.base_url = sanitize_base_url(raw_base_url)
        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        self.retries = retries
        self.backoff_factor = backoff_factor

        level = logging.getLevelName(log_level.upper()) if isinstance(log_level, str) else log_level
        configure_json_logging(level)
        logger.setLevel(level)

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "x-imn-security-key": security_key,
            },
            timeout=self.timeout,
        )

        if tracer is not None:
            self._tracer = tracer
        elif trace is not None:
            self._tracer = trace.get_tracer(__name__)
        else:
            self._tracer = None

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    def _should_retry(self, retry_state: RetryCallState) -> bool:
        if retry_state.outcome is None:
            return False
        exc = retry_state.outcome.exception()
        if isinstance(exc, (httpx.RequestError,)):
            return True
        return False

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
