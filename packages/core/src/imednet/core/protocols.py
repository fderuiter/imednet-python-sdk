"""Core protocols for the HTTP client to decouple endpoints from concrete implementations."""

from typing import Any, Awaitable, Dict, Optional, Protocol, Tuple, runtime_checkable

import httpx

from .retry import RetryPolicy


@runtime_checkable
class RequestorProtocol(Protocol):
    """Protocol for synchronous HTTP clients."""

    @property
    def retry_policy(self) -> RetryPolicy:
        """Get the retry policy."""
        ...

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        """Set the retry policy."""
        ...

    def close(self) -> None:
        """Close the underlying client."""
        ...

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a GET request."""
        ...

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a POST request."""
        ...


@runtime_checkable
class AsyncRequestorProtocol(Protocol):
    """Protocol for asynchronous HTTP clients."""

    @property
    def retry_policy(self) -> RetryPolicy:
        """Get the retry policy."""
        ...

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        """Set the retry policy."""
        ...

    def aclose(self) -> Awaitable[None]:
        """Close the underlying client."""
        ...

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Awaitable[httpx.Response]:
        """Make a GET request."""
        ...

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Awaitable[httpx.Response]:
        """Make a POST request."""
        ...


@runtime_checkable
class ClientProvider(Protocol):
    """Protocol for classes that provide access to synchronous and asynchronous clients."""

    def _require_sync_client(self) -> RequestorProtocol:
        """Return the configured sync client."""
        ...

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client."""
        ...


@runtime_checkable
class ParamProcessor(Protocol):
    """Protocol for parameter processing strategies."""

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process filters to extract special parameters.

        Args:
            filters: The dictionary of filters provided to the endpoint.

        Returns:
            A tuple containing:
            - The modified filters dictionary (for query string).
            - A dictionary of special parameters (to be merged into extra_params).
        """
        ...
