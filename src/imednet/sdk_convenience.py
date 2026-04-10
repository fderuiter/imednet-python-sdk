"""
Convenience mixin for the iMedNet SDK.

This module contains high-level helper methods that delegate to specific endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Protocol, Union

from imednet.models.codings import Coding
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.jobs import Job, JobStatus
from imednet.models.queries import Query
from imednet.models.record_revisions import RecordRevision
from imednet.models.records import Record
from imednet.models.sites import Site
from imednet.models.studies import Study
from imednet.models.subjects import Subject
from imednet.models.users import User
from imednet.models.variables import Variable
from imednet.models.visits import Visit
from imednet.workflows.job_poller import JobPoller

if TYPE_CHECKING:
    from imednet.endpoints.codings import CodingsEndpoint
    from imednet.endpoints.forms import FormsEndpoint
    from imednet.endpoints.intervals import IntervalsEndpoint
    from imednet.endpoints.jobs import JobsEndpoint
    from imednet.endpoints.queries import QueriesEndpoint
    from imednet.endpoints.record_revisions import RecordRevisionsEndpoint
    from imednet.endpoints.records import RecordsEndpoint
    from imednet.endpoints.sites import SitesEndpoint
    from imednet.endpoints.studies import StudiesEndpoint
    from imednet.endpoints.subjects import SubjectsEndpoint
    from imednet.endpoints.users import UsersEndpoint
    from imednet.endpoints.variables import VariablesEndpoint
    from imednet.endpoints.visits import VisitsEndpoint


class SDKProtocol(Protocol):
    """Protocol defining the interface required by SDKConvenienceMixin."""

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


class SDKConvenienceMixin:
    """
    Mixin class providing convenience methods for the SDK.

    These methods wrap endpoint calls to provide a flatter API surface.
    """

    def get_codings(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Coding]:
        """List codings."""
        return self.codings.list(study_key, **filters)

    def get_forms(self: SDKProtocol, study_key: str | None = None, **filters: Any) -> List[Form]:
        """List forms."""
        return self.forms.list(study_key, **filters)

    def get_intervals(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Interval]:
        """List intervals."""
        return self.intervals.list(study_key, **filters)

    def get_job(self: SDKProtocol, study_key: str, batch_id: str) -> JobStatus:
        """Get job status."""
        return self.jobs.get(study_key, batch_id)  # type: ignore

    def get_queries(self: SDKProtocol, study_key: str | None = None, **filters: Any) -> List[Query]:
        """List queries."""
        return self.queries.list(study_key, **filters)

    def get_record_revisions(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[RecordRevision]:
        """List record revisions."""
        return self.record_revisions.list(study_key, **filters)

    def get_records(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Record]:
        """List records."""
        return self.records.list(study_key, **filters)

    def get_sites(self: SDKProtocol, study_key: str | None = None, **filters: Any) -> List[Site]:
        """List sites."""
        return self.sites.list(study_key, **filters)

    def get_studies(self: SDKProtocol, **filters: Any) -> List[Study]:
        """List studies."""
        return self.studies.list(**filters)

    def get_subjects(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Subject]:
        """List subjects."""
        return self.subjects.list(study_key, **filters)

    def get_users(self: SDKProtocol, study_key: str | None = None, **filters: Any) -> List[User]:
        """List users."""
        return self.users.list(study_key, **filters)

    def get_variables(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Variable]:
        """List variables."""
        return self.variables.list(study_key, **filters)

    def get_visits(self: SDKProtocol, study_key: str | None = None, **filters: Any) -> List[Visit]:
        """List visits."""
        return self.visits.list(study_key, **filters)

    async def async_get_codings(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Coding]:
        """Asynchronously list codings."""
        return await self.codings.async_list(study_key, **filters)

    async def async_get_forms(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Form]:
        """Asynchronously list forms."""
        return await self.forms.async_list(study_key, **filters)

    async def async_get_intervals(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Interval]:
        """Asynchronously list intervals."""
        return await self.intervals.async_list(study_key, **filters)

    async def async_get_job(self: SDKProtocol, study_key: str, batch_id: str) -> JobStatus:
        """Asynchronously get job status."""
        return await self.jobs.async_get(study_key, batch_id)  # type: ignore

    async def async_get_queries(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Query]:
        """Asynchronously list queries."""
        return await self.queries.async_list(study_key, **filters)

    async def async_get_record_revisions(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[RecordRevision]:
        """Asynchronously list record revisions."""
        return await self.record_revisions.async_list(study_key, **filters)

    async def async_get_records(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Record]:
        """Asynchronously list records."""
        return await self.records.async_list(study_key, **filters)

    async def async_get_sites(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Site]:
        """Asynchronously list sites."""
        return await self.sites.async_list(study_key, **filters)

    async def async_get_studies(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Study]:
        """Asynchronously list studies."""
        return await self.studies.async_list(study_key, **filters)

    async def async_get_subjects(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Subject]:
        """Asynchronously list subjects."""
        return await self.subjects.async_list(study_key, **filters)

    async def async_get_users(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[User]:
        """Asynchronously list users."""
        return await self.users.async_list(study_key, **filters)

    async def async_get_variables(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Variable]:
        """Asynchronously list variables."""
        return await self.variables.async_list(study_key, **filters)

    async def async_get_visits(
        self: SDKProtocol, study_key: str | None = None, **filters: Any
    ) -> List[Visit]:
        """Asynchronously list visits."""
        return await self.visits.async_list(study_key, **filters)

    def create_record(
        self: SDKProtocol,
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

    def poll_job(
        self: SDKProtocol,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Poll a job until it reaches a terminal state."""

        return JobPoller(self.jobs.get, False).run(study_key, batch_id, interval, timeout)

    async def async_poll_job(
        self: SDKProtocol,
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
