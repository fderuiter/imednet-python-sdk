"""
Convenience mixin for the iMedNet SDK.

This module contains high-level helper methods that delegate to specific endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Protocol, Union

from imednet.models.jobs import Job, JobStatus
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

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically resolve get_* methods to their corresponding endpoint list() or get() calls.
        """
        if name.startswith("get_"):
            target_name = name[4:]

            # Special case for get_job
            if target_name == "job":

                def _get_job_wrapper(study_key: str, batch_id: str) -> JobStatus:
                    return self.jobs.get(study_key, batch_id)  # type: ignore

                return _get_job_wrapper

            # Special case for record_revisions
            if target_name == "record_revisions":
                target_endpoint = self.record_revisions  # type: ignore
            else:
                target_endpoint = getattr(self, target_name, None)

            if target_endpoint is not None and hasattr(target_endpoint, "list"):

                def _list_wrapper(*args: Any, **kwargs: Any) -> Any:
                    return target_endpoint.list(*args, **kwargs)

                return _list_wrapper

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

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
