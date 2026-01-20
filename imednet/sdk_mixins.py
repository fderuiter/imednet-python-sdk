"""
Mixins for the ImednetSDK.

This module contains mixins that extend the functionality of the main ImednetSDK class.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Union

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

    class SDKProtocol(Protocol):
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
    Convenience methods for ImednetSDK.

    These methods provide shortcuts to common endpoint operations.
    """

    def get_studies(self: SDKProtocol, **filters: Any) -> List[Study]:
        """Return all studies accessible by the current API key."""
        return self.studies.list(**filters)

    def get_records(
        self: SDKProtocol,
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

    def get_sites(self: SDKProtocol, study_key: str, **filters: Any) -> List[Site]:
        """Return sites for the specified study."""
        return self.sites.list(study_key, **filters)

    def get_subjects(self: SDKProtocol, study_key: str, **filters: Any) -> List[Subject]:
        """Return subjects for the specified study."""
        return self.subjects.list(study_key, **filters)

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

    def get_forms(self: SDKProtocol, study_key: str, **filters: Any) -> List[Form]:
        """Return forms for the specified study."""
        return self.forms.list(study_key, **filters)

    def get_intervals(self: SDKProtocol, study_key: str, **filters: Any) -> List[Interval]:
        """Return intervals for the specified study."""
        return self.intervals.list(study_key, **filters)

    def get_variables(self: SDKProtocol, study_key: str, **filters: Any) -> List[Variable]:
        """Return variables for the specified study."""
        return self.variables.list(study_key, **filters)

    def get_visits(self: SDKProtocol, study_key: str, **filters: Any) -> List[Visit]:
        """Return visits for the specified study."""
        return self.visits.list(study_key, **filters)

    def get_codings(self: SDKProtocol, study_key: str, **filters: Any) -> List[Coding]:
        """Return codings for the specified study."""
        return self.codings.list(study_key, **filters)

    def get_queries(self: SDKProtocol, study_key: str, **filters: Any) -> List[Query]:
        """Return queries for the specified study."""
        return self.queries.list(study_key, **filters)

    def get_record_revisions(self: SDKProtocol, study_key: str, **filters: Any) -> List[RecordRevision]:
        """Return record revisions for the specified study."""
        return self.record_revisions.list(study_key, **filters)

    def get_users(self: SDKProtocol, study_key: str, include_inactive: bool = False) -> List[User]:
        """Return users for the specified study."""
        return self.users.list(study_key, include_inactive=include_inactive)

    def get_job(self: SDKProtocol, study_key: str, batch_id: str) -> JobStatus:
        """Return job details for the specified batch."""
        return self.jobs.get(study_key, batch_id)

    def poll_job(
        self: SDKProtocol,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Poll a job until it reaches a terminal state."""
        from imednet.workflows.job_poller import JobPoller
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
        from imednet.workflows.job_poller import JobPoller
        return await JobPoller(self.jobs.async_get, True).run_async(
            study_key, batch_id, interval, timeout
        )
