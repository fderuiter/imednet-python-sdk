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

from .config import Config, load_config
from .core.async_client import AsyncClient
from .core.client import Client
from .core.context import Context
from .core.retry import RetryPolicy
from .endpoints.base import BaseEndpoint
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
from .workflows.data_extraction import DataExtractionWorkflow
from .workflows.job_poller import JobPoller
from .workflows.query_management import QueryManagementWorkflow
from .workflows.record_mapper import RecordMapper
from .workflows.record_update import RecordUpdateWorkflow
from .workflows.subject_data import SubjectDataWorkflow


class Workflows:
    """Namespace for accessing workflow classes."""

    def __init__(self, sdk_instance: "ImednetSDK"):
        self.data_extraction = DataExtractionWorkflow(sdk_instance)
        self.query_management = QueryManagementWorkflow(sdk_instance)
        self.record_mapper = RecordMapper(sdk_instance)
        self.record_update = RecordUpdateWorkflow(sdk_instance)
        self.subject_data = SubjectDataWorkflow(sdk_instance)


# Mapping of attribute names to their endpoint classes
_ENDPOINT_REGISTRY: dict[str, type[BaseEndpoint]] = {
    "codings": CodingsEndpoint,
    "forms": FormsEndpoint,
    "intervals": IntervalsEndpoint,
    "jobs": JobsEndpoint,
    "queries": QueriesEndpoint,
    "record_revisions": RecordRevisionsEndpoint,
    "records": RecordsEndpoint,
    "sites": SitesEndpoint,
    "studies": StudiesEndpoint,
    "subjects": SubjectsEndpoint,
    "users": UsersEndpoint,
    "variables": VariablesEndpoint,
    "visits": VisitsEndpoint,
}


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
        """Initialize the SDK with credentials and configuration."""

        config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)

        self._validate_env(config)

        self.config = config
        self._api_key = config.api_key
        self._security_key = config.security_key
        self._base_url = config.base_url

        self.ctx = Context()

        self._client = Client(
            api_key=config.api_key,
            security_key=config.security_key,
            base_url=config.base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            retry_policy=retry_policy,
        )
        self._async_client = (
            AsyncClient(
                api_key=config.api_key,
                security_key=config.security_key,
                base_url=config.base_url,
                timeout=timeout,
                retries=retries,
                backoff_factor=backoff_factor,
                retry_policy=retry_policy,
            )
            if enable_async
            else None
        )

        self._init_endpoints()
        self.workflows = Workflows(self)

    def _validate_env(self, config: Config) -> None:
        """Ensure required credentials are present."""
        if not config.api_key and not config.security_key:
            raise ValueError("API key and security key are required")
        elif not config.api_key:
            raise ValueError("API key is required")
        elif not config.security_key:
            raise ValueError("Security key is required")

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
        for attr, endpoint_cls in _ENDPOINT_REGISTRY.items():
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

    # ------------------------------------------------------------------
    # Convenience wrappers around common endpoint methods
    # ------------------------------------------------------------------

    def get_studies(self, **filters: Any) -> List[Study]:
        """Return all studies accessible by the current API key."""
        return self.studies.list(**filters)

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

    def get_sites(self, study_key: str, **filters: Any) -> List[Site]:
        """Return sites for the specified study."""
        return self.sites.list(study_key, **filters)

    def get_subjects(self, study_key: str, **filters: Any) -> List[Subject]:
        """Return subjects for the specified study."""
        return self.subjects.list(study_key, **filters)

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

    def get_forms(self, study_key: str, **filters: Any) -> List[Form]:
        """Return forms for the specified study."""
        return self.forms.list(study_key, **filters)

    def get_intervals(self, study_key: str, **filters: Any) -> List[Interval]:
        """Return intervals for the specified study."""
        return self.intervals.list(study_key, **filters)

    def get_variables(self, study_key: str, **filters: Any) -> List[Variable]:
        """Return variables for the specified study."""
        return self.variables.list(study_key, **filters)

    def get_visits(self, study_key: str, **filters: Any) -> List[Visit]:
        """Return visits for the specified study."""
        return self.visits.list(study_key, **filters)

    def get_codings(self, study_key: str, **filters: Any) -> List[Coding]:
        """Return codings for the specified study."""
        return self.codings.list(study_key, **filters)

    def get_queries(self, study_key: str, **filters: Any) -> List[Query]:
        """Return queries for the specified study."""
        return self.queries.list(study_key, **filters)

    def get_record_revisions(self, study_key: str, **filters: Any) -> List[RecordRevision]:
        """Return record revisions for the specified study."""
        return self.record_revisions.list(study_key, **filters)

    def get_users(self, study_key: str, include_inactive: bool = False) -> List[User]:
        """Return users for the specified study."""
        return self.users.list(study_key, include_inactive=include_inactive)

    def get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """Return job details for the specified batch."""
        return self.jobs.get(study_key, batch_id)

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
