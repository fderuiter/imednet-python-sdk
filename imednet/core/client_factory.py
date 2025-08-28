from __future__ import annotations

from typing import Optional

from ..config import Config
from .async_client import AsyncClient
from .client import Client
from .retry import RetryPolicy


class ClientFactory:
    """Factory for creating synchronous and asynchronous API clients."""

    @staticmethod
    def create(
        config: Config,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: Optional[RetryPolicy] = None,
        is_async: bool = False,
    ) -> Client | AsyncClient:
        """
        Create and configure a client.

        Args:
            config: The configuration object.
            timeout: Request timeout in seconds.
            retries: Number of retry attempts.
            backoff_factor: Factor for exponential backoff.
            retry_policy: Custom retry policy.
            is_async: Whether to create an async client.

        Returns:
            An instance of Client or AsyncClient.
        """
        client_class = AsyncClient if is_async else Client
        return client_class(
            api_key=config.api_key,
            security_key=config.security_key,
            base_url=config.base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            retry_policy=retry_policy,
        )
