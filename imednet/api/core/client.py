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
from typing import Any, Dict, Optional, cast

import httpx

from .http_client_base import HTTPClientBase

logger = logging.getLogger(__name__)


class Client(HTTPClientBase):
    """
    Core HTTP client for the iMednet API.

    Attributes:
        base_url: Base URL for API requests.
        timeout: Default timeout for requests.
        retries: Number of retry attempts for transient errors.
        backoff_factor: Multiplier for exponential backoff.
    """

    HTTPX_CLIENT_CLS = httpx.Client
    IS_ASYNC = False

    def __enter__(self) -> Client:
        """Enter the context manager.

        Returns:
            The client instance.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Exit the context manager and close the client.

        Args:
            exc_type: The exception type.
            exc: The exception instance.
            tb: The traceback.
        """
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a GET request.

        Args:
            path: URL path or full URL.
            params: Query parameters.
            **kwargs: Additional keyword arguments to pass to the HTTP client.

        Returns:
            The HTTP response.

        Raises:
            APIError: If the API returns an error.
        """
        return cast(httpx.Response, self._request("GET", path, params=params, **kwargs))

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a POST request.

        Args:
            path: URL path or full URL.
            json: JSON body for the request.
            **kwargs: Additional keyword arguments to pass to the HTTP client.

        Returns:
            The HTTP response.

        Raises:
            APIError: If the API returns an error.
        """
        return cast(httpx.Response, self._request("POST", path, json=json, **kwargs))
