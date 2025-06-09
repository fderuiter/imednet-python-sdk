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
from typing import Any, Dict, Optional, Union

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

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

    _client: Any

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

    def _process_response(self, response: httpx.Response) -> httpx.Response:
        """Validate the HTTP response and raise appropriate errors."""
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
        try:
            response = retryer(lambda: self._client.request(method, url, **kwargs))
        except RetryError as e:
            logger.error("Request failed after retries: %s", e)
            raise RequestError("Network request failed after retries")

        return self._process_response(response)

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


class AsyncClient(Client):
    """Asynchronous variant of :class:`Client` using ``httpx.AsyncClient``."""

    def __init__(
        self,
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout] = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> None:
        super().__init__(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
        )
        headers = self._client.headers
        self._client.close()
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
        )

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:  # type: ignore[override]
        """Close the underlying asynchronous HTTP client."""
        await self._client.aclose()

    async def _request_async(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Internal async request with retry logic and error handling."""
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._should_retry,
            reraise=True,
        )
        try:
            response: httpx.Response = await retryer(self._client.request, method, url, **kwargs)
        except RetryError as e:
            logger.error("Request failed after retries: %s", e)
            raise RequestError("Network request failed after retries")
        return self._process_response(response)

    async def get(  # type: ignore[override]
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an asynchronous GET request."""
        return await self._request_async("GET", path, params=params, **kwargs)

    async def post(  # type: ignore[override]
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an asynchronous POST request."""
        return await self._request_async("POST", path, json=json, **kwargs)
