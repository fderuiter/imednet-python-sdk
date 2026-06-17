"""
Factory for creating HTTP clients.

This module encapsulates the creation logic for `Client` and `AsyncClient`,
handling authentication, configuration, and retry policies.
"""

from __future__ import annotations

from imednet.auth.api_key import ApiKeyAuth
from imednet.auth.oidc import OIDCAuth
from imednet.auth.strategy import AuthStrategy
from imednet.config import Config
from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.retry import RetryPolicy


class ClientFactory:
    """Factory for creating API clients."""

    @staticmethod
    def create_client(
        config: Config,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: RetryPolicy | None = None,
    ) -> Client:
        """Create a synchronous client."""
        auth: AuthStrategy
        if config.oidc_token:
            auth = OIDCAuth(config.oidc_token)
        else:
            # Type ignore since config ensures api_key/security_key are not None here
            auth = ApiKeyAuth(config.api_key, config.security_key)  # type: ignore[arg-type]
        client = Client(
            api_key=config.api_key or "",
            security_key=config.security_key or "",
            base_url=config.base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            retry_policy=retry_policy,
            auth=auth,
        )
        client.auth = auth
        return client

    @staticmethod
    def create_async_client(
        config: Config,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: RetryPolicy | None = None,
    ) -> AsyncClient:
        """Create an asynchronous client."""
        auth: AuthStrategy
        if config.oidc_token:
            auth = OIDCAuth(config.oidc_token)
        else:
            auth = ApiKeyAuth(config.api_key, config.security_key)  # type: ignore[arg-type]
        async_client = AsyncClient(
            api_key=config.api_key or "",
            security_key=config.security_key or "",
            base_url=config.base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            retry_policy=retry_policy,
            auth=auth,
        )
        async_client.auth = auth
        return async_client
