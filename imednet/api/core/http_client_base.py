from __future__ import annotations

import logging
from typing import Any, Awaitable, Optional, Type, Union, cast

import httpx

from ._requester import RequestExecutor
from .base_client import BaseClient, Tracer
from .retry import RetryPolicy

logger = logging.getLogger(__name__)


class HTTPClientBase(BaseClient):
    """Shared logic for synchronous and asynchronous HTTP clients."""

    HTTPX_CLIENT_CLS: Type[httpx.Client | httpx.AsyncClient]
    IS_ASYNC: bool

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
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        """Initializes the HTTPClientBase.

        Args:
            api_key: The API key for authentication.
            security_key: The security key for authentication.
            base_url: The base URL of the iMednet API.
            timeout: The timeout for HTTP requests.
            retries: The number of times to retry a failed request.
            backoff_factor: The backoff factor for retries.
            log_level: The logging level.
            tracer: The OpenTelemetry tracer to use.
            retry_policy: The retry policy to use.
        """
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
            is_async=self.IS_ASYNC,
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            tracer=self._tracer,
            retry_policy=retry_policy,
        )

    def _create_client(self, api_key: str, security_key: str) -> httpx.Client | httpx.AsyncClient:
        """Create and configure the underlying httpx client.

        Args:
            api_key: The API key.
            security_key: The security key.

        Returns:
            An instance of `httpx.Client` or `httpx.AsyncClient`.
        """
        return self.HTTPX_CLIENT_CLS(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "x-imn-security-key": security_key,
            },
            timeout=self.timeout,
        )

    @property
    def retry_policy(self) -> RetryPolicy:
        """The retry policy used for requests."""
        return cast(RetryPolicy, self._executor.retry_policy)

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        """Set the retry policy.

        Args:
            policy: The new retry policy.
        """
        self._executor.retry_policy = policy

    def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Awaitable[httpx.Response] | httpx.Response:
        """Make a request using the request executor.

        Args:
            method: The HTTP method.
            path: The URL path.
            **kwargs: Additional keyword arguments to pass to the executor.

        Returns:
            A response or an awaitable response.
        """
        return self._executor(method, path, **kwargs)
