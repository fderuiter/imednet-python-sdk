"""
Core HTTP client for interacting with the iMednet REST API.

This module defines the `Client` class which handles:
- Authentication headers (API key and security key).
- Configuration of base URL, timeouts, and retry logic.
- Making HTTP GET and POST requests.
- Error mapping to custom exceptions.
- Context-manager support for automatic cleanup.
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import nullcontext
from types import TracebackType
from typing import Any, Dict, Optional, Union

try:  # opentelemetry is optional
    from opentelemetry import trace
    from opentelemetry.trace import Tracer
except Exception:  # pragma: no cover - optional dependency
    trace = None
    Tracer = None
import httpx
from tenacity import (
    RetryCallState,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

from imednet.core.exceptions import (
    ApiError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
    UnauthorizedError,
)
from imednet.utils import sanitize_base_url
from imednet.utils.json_logging import configure_json_logging

logger = logging.getLogger(__name__)


STATUS_TO_ERROR: dict[int, type[ApiError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


class Client:
    """
    Core HTTP client for the iMednet API.

    Attributes:
        base_url: Base URL for API requests.
        timeout: Default timeout for requests.
        retries: Number of retry attempts for transient errors.
        backoff_factor: Multiplier for exponential backoff.
    """

    DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"

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
    ):
        """
        Initialize the HTTP client.

        Credentials can be supplied directly or via environment variables
        `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY`. If `base_url` is not
        provided, the `IMEDNET_BASE_URL` environment variable will be used if
        present.

        Args:
            api_key: iMednet API key.
            security_key: iMednet security key.
            base_url: Base URL for API; uses default if None.
            timeout: Request timeout in seconds or httpx.Timeout.
            retries: Max retry attempts for transient errors.
            backoff_factor: Factor for exponential backoff between retries.
            log_level: Logging level or name.
            tracer: Optional OpenTelemetry tracer to record spans.
        """
        api_key = (api_key or os.getenv("IMEDNET_API_KEY") or "").strip()
        security_key = (security_key or os.getenv("IMEDNET_SECURITY_KEY") or "").strip()
        if not api_key or not security_key:
            raise ValueError("API key and security key are required")

        self.base_url = base_url or os.getenv("IMEDNET_BASE_URL") or self.DEFAULT_BASE_URL
        self.base_url = self.base_url.rstrip("/")
        if self.base_url.endswith("/api"):
            self.base_url = self.base_url[:-4]

        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        self.retries = retries
        self.backoff_factor = backoff_factor

        level = logging.getLevelName(log_level.upper()) if isinstance(log_level, str) else log_level
        configure_json_logging(level)
        logger.setLevel(level)

        self._client = httpx.Client(
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

    def __enter__(self) -> Client:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def _should_retry(self, retry_state: RetryCallState) -> bool:
        """Determine whether to retry based on exception type and attempt count."""
        if retry_state.outcome is None:
            return False
        exc = retry_state.outcome.exception()
        if isinstance(exc, (httpx.RequestError,)):
            return True
        return False

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Internal request with retry logic and error handling.
        """
        retryer = Retrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._should_retry,
            reraise=True,
        )

        span_cm = (
            self._tracer.start_as_current_span(
                "http_request",
                attributes={"endpoint": url, "method": method},
            )
            if self._tracer
            else nullcontext()
        )

        with span_cm as span:
            try:
                start = time.monotonic()
                response = retryer(lambda: self._client.request(method, url, **kwargs))
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

        # HTTP error handling
        if response.is_error:
            status = response.status_code
            try:
                body = response.json()
            except Exception:
                body = response.text
            exc_cls = STATUS_TO_ERROR.get(status)
            if exc_cls:
                raise exc_cls(body)
            if 500 <= status < 600:
                raise ServerError(body)
            raise ApiError(body)

        return response

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make a GET request.

        Args:
            path: URL path or full URL.
            params: Query parameters.
        """
        return self._request("GET", path, params=params, **kwargs)

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make a POST request.

        Args:
            path: URL path or full URL.
            json: JSON body for the request.
        """
        return self._request("POST", path, json=json, **kwargs)
