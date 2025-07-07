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
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Union, cast

import httpx
from tenacity import RetryCallState

from ._requester import RequestExecutor
from .base_client import BaseClient, Tracer

logger = logging.getLogger(__name__)


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
        self._executor = RequestExecutor(
            lambda *a, **kw: self._client.request(*a, **kw),
            is_async=False,
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            tracer=self._tracer,
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

    @property
    def _should_retry(self) -> Callable[[RetryCallState], bool]:
        return self._executor.should_retry or self._executor._default_should_retry

    @_should_retry.setter
    def _should_retry(self, func: Callable[[RetryCallState], bool]) -> None:
        self._executor.should_retry = func

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
        return cast(httpx.Response, self._executor("GET", path, params=params, **kwargs))

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
        return cast(httpx.Response, self._executor("POST", path, json=json, **kwargs))
