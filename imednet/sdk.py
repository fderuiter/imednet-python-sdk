"""
Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union

from deprecation import deprecated

from .config import Config, load_config_from_env
from .core.async_client import AsyncClient
from .core.client import Client
from .core.client_factory import ClientFactory
from .core.context import Context
from .core.retry import RetryPolicy
from .endpoints.codings import CodingsEndpoint
from .endpoints.forms import FormsEndpoint
from .endpoints.intervals import IntervalsEndpoint
from .endpoints.jobs import JobsEndpoint
from .endpoints.queries import QueriesEndpoint
from .endpoints.record_revisions import RecordRevisionsEndpoint
from .endpoints.records import RecordsEndpoint
from .endpoints.registry import get_endpoint_registry
from .endpoints.sites import SitesEndpoint
from .endpoints.studies import StudiesEndpoint
from .endpoints.subjects import SubjectsEndpoint
from .endpoints.users import UsersEndpoint
from .endpoints.variables import VariablesEndpoint
from .endpoints.visits import VisitsEndpoint
from .models.codings import Coding
from .models.forms import Form
from .models.intervals import Interval
from .models.jobs import Job, JobStatus
from .models.queries import Query
from .models.record_revisions import RecordRevision
from .models.records import Record
from .models.sites import Site
from .models.studies import Study
from .models.subjects import Subject
from .models.users import User
from .models.variables import Variable
from .models.visits import Visit

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
        return self._client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        self._client.retry_policy = policy
        if self._async_client is not None:
            self._async_client.retry_policy = policy

    def _init_endpoints(self) -> None:
        """Instantiate and attach endpoint clients."""
        assert isinstance(self._client, Client)
        assert isinstance(self._async_client, AsyncClient) or self._async_client is None

        for attr, endpoint_cls in get_endpoint_registry().items():
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
        if self._async_client is not None:
            assert isinstance(self._async_client, AsyncClient)
            await self._async_client.aclose()
        if isinstance(self._client, Client):
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

    # ------------------------------------------------------------------
    # Convenience wrappers around common endpoint methods
    # ------------------------------------------------------------------

    @deprecated(deprecated_in="0.2.0", details="Use the `studies.list` method instead.")
    def get_studies(self, **filters: Any) -> List[Study]:
        """Return all studies accessible by the current API key."""
        return self.studies.list(**filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `records.list` method instead.")
    def get_records(
        self,
        study_key: str,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> List[Record]:
        """Return records for the specified study."""
        return self.records.list(
            study_key=study_key,
            record_data_filter=record_data_filter,
            **filters,
        )

    @deprecated(deprecated_in="0.2.0", details="Use the `sites.list` method instead.")
    def get_sites(self, study_key: str, **filters: Any) -> List[Site]:
        """Return sites for the specified study."""
        return self.sites.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `subjects.list` method instead.")
    def get_subjects(self, study_key: str, **filters: Any) -> List[Subject]:
        """Return subjects for the specified study."""
        return self.subjects.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `records.create` method instead.")
    def create_record(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
    ) -> Job:
        """Create records in the specified study."""
        return self.records.create(
            study_key,
            records_data,
            email_notify=email_notify,
        )

    @deprecated(deprecated_in="0.2.0", details="Use the `forms.list` method instead.")
    def get_forms(self, study_key: str, **filters: Any) -> List[Form]:
        """Return forms for the specified study."""
        return self.forms.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `intervals.list` method instead.")
    def get_intervals(self, study_key: str, **filters: Any) -> List[Interval]:
        """Return intervals for the specified study."""
        return self.intervals.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `variables.list` method instead.")
    def get_variables(self, study_key: str, **filters: Any) -> List[Variable]:
        """Return variables for the specified study."""
        return self.variables.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `visits.list` method instead.")
    def get_visits(self, study_key: str, **filters: Any) -> List[Visit]:
        """Return visits for the specified study."""
        return self.visits.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `codings.list` method instead.")
    def get_codings(self, study_key: str, **filters: Any) -> List[Coding]:
        """Return codings for the specified study."""
        return self.codings.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `queries.list` method instead.")
    def get_queries(self, study_key: str, **filters: Any) -> List[Query]:
        """Return queries for the specified study."""
        return self.queries.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `record_revisions.list` method instead.")
    def get_record_revisions(self, study_key: str, **filters: Any) -> List[RecordRevision]:
        """Return record revisions for the specified study."""
        return self.record_revisions.list(study_key, **filters)

    @deprecated(deprecated_in="0.2.0", details="Use the `users.list` method instead.")
    def get_users(self, study_key: str, include_inactive: bool = False) -> List[User]:
        """Return users for the specified study."""
        return self.users.list(study_key, include_inactive=include_inactive)

    @deprecated(deprecated_in="0.2.0", details="Use the `jobs.get` method instead.")
    def get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """Return job details for the specified batch."""
        return self.jobs.get(study_key, batch_id)

    @deprecated(deprecated_in="0.2.0", details="Use the `JobPoller` class directly.")
    def poll_job(
        self,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Poll a job until it reaches a terminal state."""

        return JobPoller(self.jobs.get, False).run(study_key, batch_id, interval, timeout)

    @deprecated(deprecated_in="0.2.0", details="Use the `JobPoller` class directly.")
    async def async_poll_job(
        self,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Asynchronously poll a job until it reaches a terminal state."""

        return await JobPoller(self.jobs.async_get, True).run_async(
            study_key, batch_id, interval, timeout
        )


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
