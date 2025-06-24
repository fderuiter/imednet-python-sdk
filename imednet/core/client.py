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
import time
from contextlib import nullcontext
from types import TracebackType
from typing import Any, Dict, Optional, Union

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

from .base_client import BaseClient, Tracer

logger = logging.getLogger(__name__)


STATUS_TO_ERROR: dict[int, type[ApiError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


class Client(BaseClient):
    """
    Core HTTP client for the iMednet API.

    Attributes:
        base_url: Base URL for API requests.
        timeout: Default timeout for requests.
        retries: Number of retry attempts for transient errors.
        backoff_factor: Multiplier for exponential backoff.
    """

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

    def _create_client(self, api_key: str, security_key: str) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "x-imn-security-key": security_key,
            },
            timeout=self.timeout,
        )

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
