"""Endpoint for checking job status in a study."""

from typing import Awaitable, List, cast

from imednet.core.paginator import AsyncJsonListPaginator, JsonListPaginator
from imednet.endpoints._mixins import ListEndpointMixin, PathGetEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job, JobStatus


class JobsEndpoint(BaseEndpoint, ListEndpointMixin[JobStatus], PathGetEndpointMixin[JobStatus]):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    This endpoint provides methods to fetch individual job status by batch ID
    and list all jobs for a study.
    """

    PATH = "jobs"
    MODEL = JobStatus

    def get(self, study_key: str, batch_id: str) -> JobStatus:
        """
        Get a specific job by batch ID.

        Args:
            study_key: Study identifier
            batch_id: Batch ID of the job

        Returns:
            JobStatus object with current state and timestamps
        """
        return cast(
            JobStatus,
            self._get_impl_path(self._client, study_key=study_key, item_id=batch_id),
        )

    async def async_get(self, study_key: str, batch_id: str) -> JobStatus:
        """Asynchronously get a specific job by batch ID."""
        return await cast(
            Awaitable[JobStatus],
            self._get_impl_path(
                self._require_async_client(), study_key=study_key, item_id=batch_id
            ),
        )

    def list(self, study_key: str) -> List[Job]:
        """
        List all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        return cast(
            List[Job],
            self._list_impl(self._client, JsonListPaginator, study_key=study_key),
        )

    async def async_list(self, study_key: str) -> List[Job]:
        """Asynchronously list all jobs for a specific study."""
        return await cast(
            Awaitable[List[Job]],
            self._list_impl(
                self._require_async_client(), AsyncJsonListPaginator, study_key=study_key
            ),
        )
