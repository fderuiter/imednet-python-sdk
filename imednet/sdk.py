"""
Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from .api.core.async_client import AsyncClient
from .api.core.client import Client
from .api.core.client_factory import ClientFactory
from .api.core.context import Context
from .api.core.retry import RetryPolicy
from .api.endpoints.codings import CodingsEndpoint
from .api.endpoints.forms import FormsEndpoint
from .api.endpoints.intervals import IntervalsEndpoint
from .api.endpoints.jobs import JobsEndpoint
from .api.endpoints.queries import QueriesEndpoint
from .api.endpoints.record_revisions import RecordRevisionsEndpoint
from .api.endpoints.records import RecordsEndpoint
from .api.endpoints.registry import get_endpoint_registry
from .api.endpoints.sites import SitesEndpoint
from .api.endpoints.studies import StudiesEndpoint
from .api.endpoints.subjects import SubjectsEndpoint
from .api.endpoints.users import UsersEndpoint
from .api.endpoints.variables import VariablesEndpoint
from .api.endpoints.visits import VisitsEndpoint
from .api.models.jobs import JobStatus
from .config import Config, load_config_from_env

# Import workflow classes
from .workflows import Workflows
from .workflows.job_poller import JobPoller


class ImednetSDK:
    """
    Public entry-point for library users.

    Provides access to all iMednet API endpoints and maintains configuration.

    Attributes:
        ctx: Context object for storing state across SDK calls.
        etc...
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
    ) -> None:
        """Initializes the ImednetSDK.

        Args:
            api_key: The API key for authentication.
            security_key: The security key for authentication.
            base_url: The base URL of the iMednet API.
            timeout: The timeout for HTTP requests.
            retries: The number of times to retry a failed request.
            backoff_factor: The backoff factor for retries.
            retry_policy: The retry policy to use.
            enable_async: If `True`, the async client will be enabled.
        """
        self.config = load_config_from_env(
            api_key=api_key, security_key=security_key, base_url=base_url
        )

        self.ctx = Context()
        self._client = ClientFactory.create(
            self.config, timeout, retries, backoff_factor, retry_policy
        )
        self._async_client = (
            ClientFactory.create(
                self.config, timeout, retries, backoff_factor, retry_policy, is_async=True
            )
            if enable_async
            else None
        )

        self._init_endpoints()
        self.workflows = Workflows(self)

    @property
    def retry_policy(self) -> RetryPolicy:
        """The retry policy used for requests."""
        return self._client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        """Set the retry policy for both sync and async clients.

        Args:
            policy: The new retry policy.
        """
        self._client.retry_policy = policy
        if self._async_client is not None:
            self._async_client.retry_policy = policy

    def _init_endpoints(self) -> None:
        """Instantiate and attach all registered endpoint clients to the SDK instance."""
        assert isinstance(self._client, Client)
        assert isinstance(self._async_client, AsyncClient) or self._async_client is None

        for attr, endpoint_cls in get_endpoint_registry().items():
            setattr(self, attr, endpoint_cls(self._client, self.ctx, self._async_client))

    def __enter__(self) -> ImednetSDK:
        """Support for context manager protocol."""
        return self

    async def __aenter__(self) -> "ImednetSDK":
        """Support for async context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup resources when exiting context."""
        self.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup resources when exiting async context."""
        await self.aclose()

    def close(self) -> None:
        """Close the client connection and free resources."""
        if isinstance(self._client, Client):
            self._client.close()
        if self._async_client is not None:
            assert isinstance(self._async_client, AsyncClient)
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
        """Close the async client connection and free resources."""
        if self._async_client is not None:
            assert isinstance(self._async_client, AsyncClient)
            await self._async_client.aclose()
        if isinstance(self._client, Client):
            self._client.close()

    def get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """Get a specific job by batch ID."""
        return self.jobs.get(study_key, batch_id)

    async def async_get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """Asynchronously get a specific job by batch ID."""
        return await self.jobs.async_get(study_key, batch_id)

    def poll_job(
        self,
        study_key: str,
        batch_id: str,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Poll a job until it reaches a terminal state."""
        poller = JobPoller(self.jobs.get, is_async=False)
        return poller.run(study_key, batch_id, interval=interval, timeout=timeout)

    async def async_poll_job(
        self,
        study_key: str,
        batch_id: str,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Asynchronously poll a job until it reaches a terminal state."""
        poller = JobPoller(self.jobs.async_get, is_async=True)
        return await poller.run_async(study_key, batch_id, interval=interval, timeout=timeout)

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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the AsyncImednetSDK.

        This is a thin wrapper around the `ImednetSDK` constructor that
        forces `enable_async` to `True`.

        Args:
            *args: Positional arguments to pass to the `ImednetSDK` constructor.
            **kwargs: Keyword arguments to pass to the `ImednetSDK` constructor.
        """
        kwargs["enable_async"] = True
        super().__init__(*args, **kwargs)

    async def __aenter__(self) -> "AsyncImednetSDK":
        """Support for async context manager protocol."""
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)


__all__ = ["ImednetSDK", "AsyncImednetSDK"]
