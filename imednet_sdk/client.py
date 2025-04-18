from typing import Any, Dict, Optional

import httpx


class ImednetClient:
    """Core HTTP client for interacting with the iMednet API."""

    DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"

    def __init__(
        self,
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 30.0,  # Default timeout
    ):
        """Initializes the ImednetClient.

        Args:
            api_key: Your iMednet API key.
            security_key: Your iMednet Security key.
            base_url: The base URL for the iMednet API. Defaults to production.
            timeout: Default request timeout in seconds.
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self._api_key = api_key
        self._security_key = security_key

        self._default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
            "x-imn-security-key": self._security_key,
        }

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=timeout,
            # Add transport configuration for retries later if needed
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Internal method to make HTTP requests.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path (e.g., '/studies').
            params: URL query parameters.
            json: Request body data (for POST/PUT).
            **kwargs: Additional arguments passed to httpx.request.

        Returns:
            The httpx Response object.

        Raises:
            httpx.HTTPStatusError: For 4xx or 5xx responses.
        """
        # Ensure endpoint starts with a slash if needed, httpx handles joining
        url = endpoint

        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                **kwargs,  # Pass through extra httpx options
            )
            response.raise_for_status()  # Raise exception for bad status codes
            return response
        except httpx.RequestError as exc:
            # Handle connection errors, timeouts, etc.
            # Re-raise or wrap in a custom exception (TBD in error handling task)
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            raise
        except httpx.HTTPStatusError as exc:
            # Handle 4xx/5xx errors
            # Re-raise or wrap (TBD in error handling task)
            print(
                f"Error response {exc.response.status_code} "
                f"while requesting {exc.request.url!r}: {exc.response.text}"
            )
            # For now, return the response to allow tests to check status code
            # In real usage, we'd likely raise a custom exception here.
            # return exc.response
            raise  # Re-raise for now until proper error handling is defined

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Sends a GET request."""
        return self._request("GET", endpoint, params=params, **kwargs)

    def _post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Sends a POST request."""
        return self._request("POST", endpoint, json=json, **kwargs)

    # Public methods (can be added later as specific endpoints are implemented)
    # def get_studies(self, ...): return self._get('/studies', ...)

    def close(self):
        """Closes the underlying HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
