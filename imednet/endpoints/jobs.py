"""Endpoint for checking job status in a study."""

from typing import Any, Awaitable, Optional, cast

from imednet.core.endpoint.mixins import ListEndpoint, PathGetEndpointMixin
from imednet.core.paginator import AsyncJsonListPaginator, JsonListPaginator
from imednet.models.jobs import JobStatus


class JobsEndpoint(ListEndpoint[JobStatus], PathGetEndpointMixin[JobStatus]):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    This endpoint provides methods to fetch individual job status by batch ID
    and list all jobs for a study.
    """

    PATH = "jobs"
    MODEL = JobStatus
    PAGINATOR_CLS = JsonListPaginator
    ASYNC_PAGINATOR_CLS = AsyncJsonListPaginator

    def _raise_not_found(self, study_key: Optional[str], item_id: Any) -> None:
        raise ValueError(f"Job {item_id} not found in study {study_key}")

    def get(self, study_key: str, batch_id: str) -> JobStatus:
        """
        Get a specific job by batch ID.

        This method performs a direct API request using the provided
        ``batch_id``; it does not use caching or the ``refresh`` flag.

        Args:
            study_key: Study identifier
            batch_id: Batch ID of the job

        Returns:
            JobStatus object with current state and timestamps

        Raises:
            ValueError: If the job is not found
        """
        return cast(
            JobStatus,
            self._get_impl_path(self._client, study_key=study_key, item_id=batch_id),
        )

    async def async_get(self, study_key: str, batch_id: str) -> JobStatus:
        """
        Asynchronously get a specific job by batch ID.

        This is the async variant of :meth:`get`. Like the sync version,
        it issues a direct request by ``batch_id`` without any caching.

        Args:
            study_key: Study identifier
            batch_id: Batch ID of the job

        Returns:
            JobStatus object with current state and timestamps

        Raises:
            ValueError: If the job is not found
        """
        client = self._require_async_client()
        return await cast(
            Awaitable[JobStatus],
            self._get_impl_path(client, study_key=study_key, item_id=batch_id, is_async=True),
        )
