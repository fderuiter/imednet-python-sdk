import random
import time
from typing import Any, Dict, Optional, Set, Union

import httpx

# Type alias for timeout configuration
TimeoutTypes = Union[float, httpx.Timeout, None]

# Define retryable exceptions and status codes
DEFAULT_RETRYABLE_STATUS_CODES: Set[int] = {500, 502, 503, 504}
DEFAULT_RETRYABLE_METHODS: Set[str] = {
    "GET",
    "POST",
}  # Assuming POST is idempotent or safe to retry for this API
DEFAULT_RETRYABLE_EXCEPTIONS: Set[type] = {httpx.ConnectError, httpx.ReadTimeout, httpx.PoolTimeout}


class ImednetClient:
    """Core HTTP client for interacting with the iMednet API."""

    DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"

    def __init__(
        self,
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        timeout: TimeoutTypes = httpx.Timeout(30.0, connect=5.0),
        retries: int = 3,
        backoff_factor: float = 0.5,  # Default backoff factor (e.g., 0.5, 1, 1.5, ... seconds)
        retry_statuses: Optional[Set[int]] = None,
        retry_methods: Optional[Set[str]] = None,
        retry_exceptions: Optional[Set[type]] = None,
    ):
        """Initializes the ImednetClient.

        Args:
            api_key: Your iMednet API key.
            security_key: Your iMednet Security key.
            base_url: The base URL for the iMednet API. Defaults to production.
            timeout: Default request timeout configuration.
            retries: Number of retry attempts for transient errors.
            backoff_factor: Factor to determine delay between retries
                            (delay = backoff_factor * (2 ** attempt)).
            retry_statuses: Set of HTTP status codes to retry on.
                            Defaults to {500, 502, 503, 504}.
            retry_methods: Set of HTTP methods to allow retries for.
                           Defaults to {"GET", "POST"}.
            retry_exceptions: Set of httpx exception types to retry on.
                              Defaults to {ConnectError, ReadTimeout, PoolTimeout}.
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self._api_key = api_key
        self._security_key = security_key
        self._default_timeout = timeout
        self._retries = retries
        self._backoff_factor = backoff_factor
        self._retry_statuses = (
            retry_statuses if retry_statuses is not None else DEFAULT_RETRYABLE_STATUS_CODES
        )
        self._retry_methods = (
            retry_methods if retry_methods is not None else DEFAULT_RETRYABLE_METHODS
        )
        self._retry_exceptions = (
            retry_exceptions if retry_exceptions is not None else DEFAULT_RETRYABLE_EXCEPTIONS
        )

        self._default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
            "x-imn-security-key": self._security_key,
        }

        # Note: httpx's built-in retries via HTTPTransport are more robust,
        # but implementing manually for now as per original structure.
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self._default_timeout,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: TimeoutTypes = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Internal method to make HTTP requests with retry logic."""
        url = endpoint
        request_timeout = timeout if timeout is not None else self._default_timeout
        last_exception: Optional[Exception] = None

        for attempt in range(self._retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=request_timeout,
                    **kwargs,
                )
                # Raise HTTPStatusError for non-2xx responses
                response.raise_for_status()
                # Success!
                return response

            except httpx.HTTPStatusError as exc:
                last_exception = exc
                status = exc.response.status_code
                # Check if we should retry based on status code and method
                if (
                    attempt < self._retries
                    and status in self._retry_statuses
                    and method.upper() in self._retry_methods
                ):
                    delay = self._calculate_backoff(attempt)
                    time.sleep(delay)
                    continue  # Retry
                else:
                    raise  # Non-retryable status/method or max retries reached

            except httpx.RequestError as exc:
                last_exception = exc
                # Check if we should retry based on exception type and method
                if (
                    attempt < self._retries
                    and type(exc) in self._retry_exceptions
                    and method.upper() in self._retry_methods
                ):
                    delay = self._calculate_backoff(attempt)
                    time.sleep(delay)
                    continue  # Retry
                else:
                    raise  # Non-retryable exception/method or max retries reached

        # Should be unreachable if retries >= 0, but satisfy type checker
        # and handle edge case of retries < 0
        if last_exception:
            raise last_exception
        else:
            # This case should ideally never happen in normal flow
            raise RuntimeError("Request failed without capturing an exception after retries.")

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculates exponential backoff delay with jitter."""
        if attempt == 0:
            return 0  # No delay for the first retry
        base_delay = self._backoff_factor * (2 ** (attempt - 1))
        # Add jitter: delay +/- 50% of base delay
        jitter = random.uniform(-0.5, 0.5) * base_delay
        return max(0, base_delay + jitter)

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: TimeoutTypes = None,  # Add timeout parameter
        **kwargs: Any,
    ) -> httpx.Response:
        """Sends a GET request."""
        return self._request("GET", endpoint, params=params, timeout=timeout, **kwargs)

    def _post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        timeout: TimeoutTypes = None,  # Add timeout parameter
        **kwargs: Any,
    ) -> httpx.Response:
        """Sends a POST request."""
        return self._request("POST", endpoint, json=json, timeout=timeout, **kwargs)

    def close(self):
        """Closes the underlying HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
