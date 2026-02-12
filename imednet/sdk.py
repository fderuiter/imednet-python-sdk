"""
Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

from .config import Config, load_config
from .core.context import Context
from .core.factory import ClientFactory
from .core.retry import RetryPolicy
from .endpoints.registry import ENDPOINT_REGISTRY
from .sdk_convenience import SDKConvenienceMixin
from .workflows.namespace import Workflows

if TYPE_CHECKING:
    from .core.async_client import AsyncClient
    from .core.client import Client
    from .endpoints.codings import CodingsEndpoint
    from .endpoints.forms import FormsEndpoint
    from .endpoints.intervals import IntervalsEndpoint
    from .endpoints.jobs import JobsEndpoint
    from .endpoints.queries import QueriesEndpoint
    from .endpoints.record_revisions import RecordRevisionsEndpoint
    from .endpoints.records import RecordsEndpoint
    from .endpoints.sites import SitesEndpoint
    from .endpoints.studies import StudiesEndpoint
    from .endpoints.subjects import SubjectsEndpoint
    from .endpoints.users import UsersEndpoint
    from .endpoints.variables import VariablesEndpoint
    from .endpoints.visits import VisitsEndpoint


class ImednetSDK(SDKConvenienceMixin):
    """
    Public entry-point for library users.

    Provides access to all iMednet API endpoints and maintains configuration.
    """

    codings: CodingsEndpoint
    forms: FormsEndpoint
    intervals: IntervalsEndpoint
    jobs: JobsEndpoint
    queries: QueriesEndpoint
    record_revisions: RecordRevisionsEndpoint
    records: RecordsEndpoint
    sites: SitesEndpoint
    studies: StudiesEndpoint
    subjects: SubjectsEndpoint
    users: UsersEndpoint
    variables: VariablesEndpoint
    visits: VisitsEndpoint
    config: Config

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: RetryPolicy | None = None,
        enable_async: bool = False,
        client: Optional[Client] = None,
        async_client: Optional[AsyncClient] = None,
    ) -> None:
        """Initialize the SDK with credentials and configuration."""

        config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)

        self.config = config
        self._api_key = config.api_key
        self._security_key = config.security_key
        self._base_url = config.base_url

        self.ctx = Context()

        self._init_clients(
            config,
            client,
            async_client,
            enable_async,
            timeout,
            retries,
            backoff_factor,
            retry_policy,
        )

        self._init_endpoints()
        self.workflows = Workflows(self)

    def _init_clients(
        self,
        config: Config,
        client: Optional[Client],
        async_client: Optional[AsyncClient],
        enable_async: bool,
        timeout: float,
        retries: int,
        backoff_factor: float,
        retry_policy: RetryPolicy | None,
    ) -> None:
        """Initialize sync and async clients."""
        if client:
            self._client = client
        else:
            self._client = ClientFactory.create_client(
                config=config,
                timeout=timeout,
                retries=retries,
                backoff_factor=backoff_factor,
                retry_policy=retry_policy,
            )

        if async_client:
            self._async_client: Optional[AsyncClient] = async_client
        elif enable_async:
            self._async_client = ClientFactory.create_async_client(
                config=config,
                timeout=timeout,
                retries=retries,
                backoff_factor=backoff_factor,
                retry_policy=retry_policy,
            )
        else:
            self._async_client = None

    @property
    def retry_policy(self) -> RetryPolicy:
        return self._client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        self._client.retry_policy = policy
        if self._async_client is not None:
            self._async_client.retry_policy = policy

    def _init_endpoints(self) -> None:
        """Instantiate endpoint clients."""
        for attr, endpoint_cls in ENDPOINT_REGISTRY.items():
            setattr(self, attr, endpoint_cls(self._client, self.ctx, self._async_client))

    def __enter__(self) -> ImednetSDK:
        """Support for context manager protocol."""
        return self

    async def __aenter__(self) -> "ImednetSDK":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup resources when exiting context."""
        self.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()

    def close(self) -> None:
        """Close the client connection and free resources."""
        self._client.close()
        if self._async_client is not None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, safe to use asyncio.run
                asyncio.run(self._async_client.aclose())
            else:
                if loop.is_closed():
                    asyncio.run(self._async_client.aclose())
                else:
                    loop.run_until_complete(self._async_client.aclose())

    async def aclose(self) -> None:
        if self._async_client is not None:
            await self._async_client.aclose()
        self._client.close()

    def set_default_study(self, study_key: str) -> None:
        """
        Set the default study key for subsequent API calls.

        Args:
            study_key: The study key to use as default.
        """
        self.ctx.set_default_study_key(study_key)

    def clear_default_study(self) -> None:
        """Clear the default study key."""
        self.ctx.clear_default_study_key()


class AsyncImednetSDK(ImednetSDK):
    """Async variant of :class:`ImednetSDK` using the async HTTP client."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - thin wrapper
        kwargs["enable_async"] = True
        super().__init__(*args, **kwargs)

    async def __aenter__(self) -> "AsyncImednetSDK":
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)


__all__ = ["ImednetSDK", "AsyncImednetSDK"]
