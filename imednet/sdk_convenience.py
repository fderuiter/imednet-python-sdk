"""
Convenience mixin for the ImednetSDK.

This module contains shortcut methods for common API operations, keeping the main
SDK class focused on configuration and lifecycle management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

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
from .workflows.job_poller import JobPoller

if TYPE_CHECKING:
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


class ImednetSDKConvenienceMixin:
    """Mixin containing convenience wrappers for common endpoint methods."""

    # Type hints for the mixin consumer (ImednetSDK)
    if TYPE_CHECKING:
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
