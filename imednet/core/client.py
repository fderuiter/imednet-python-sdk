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
from typing import Any, Dict, Optional, Union

import httpx
from tenacity import RetryCallState, RetryError, Retrying, stop_after_attempt, wait_exponential

from imednet import metrics
from imednet.core.exceptions import (
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
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout] = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        """
        Initialize the HTTP client.

        Args:
            api_key: iMednet API key.
            security_key: iMednet security key.
            base_url: Base URL for API; uses default if None.
            timeout: Request timeout in seconds or httpx.Timeout.
            retries: Max retry attempts for transient errors.
            backoff_factor: Factor for exponential backoff between retries.
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        self.retries = retries
        self.backoff_factor = backoff_factor

        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "x-imn-security-key": security_key,
            },
            timeout=self.timeout,
            trust_env=False,
        )

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
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

        start_time = time.perf_counter()
        try:
            response = retryer(lambda: self._client.request(method, url, **kwargs))
        except RetryError as e:
            logger.error("Request failed after retries: %s", e)
            raise RequestError("Network request failed after retries")
        finally:
            if metrics.metrics_enabled and metrics.API_CALLS and metrics.API_LATENCY:
                elapsed = time.perf_counter() - start_time
                metrics.API_CALLS.labels(method=method, endpoint=url).inc()
                metrics.API_LATENCY.labels(method=method, endpoint=url).observe(elapsed)

        # HTTP error handling
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
