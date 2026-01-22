"""Endpoint for checking job status in a study."""

import inspect
from typing import Any, List

from imednet.core.paginator import AsyncSimpleListPaginator, SimpleListPaginator
from imednet.endpoints._mixins import ListEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job, JobStatus


class JobsEndpoint(BaseEndpoint, ListEndpointMixin[Job]):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    Provides a method to fetch a job by its batch ID.
    """

    PATH = "jobs"
    MODEL = Job

    def _get_impl(self, client: Any, study_key: str, batch_id: str) -> Any:
        endpoint = self._build_path(study_key, "jobs", batch_id)
        if inspect.iscoroutinefunction(client.get):

            async def _async() -> JobStatus:
                response = await client.get(endpoint)
                data = response.json()
                if not data:
                    raise ValueError(f"Job {batch_id} not found in study {study_key}")
                return JobStatus.from_json(data)

            return _async()

        response = client.get(endpoint)
        data = response.json()
        if not data:
            raise ValueError(f"Job {batch_id} not found in study {study_key}")
        return JobStatus.from_json(data)

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
        """
        result = self._get_impl(self._client, study_key, batch_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, batch_id: str) -> JobStatus:
        """Asynchronous version of :meth:`get`.

        Like the sync variant, it simply issues a request by ``batch_id``
        without any caching.
        """
        client = self._require_async_client()
        return await self._get_impl(client, study_key, batch_id)

    def list(self, study_key: str) -> List[Job]:
        """
        List all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        # We use SimpleListPaginator because the API returns a flat list
        # without pagination metadata.
        return self._list_impl(
            self._client,
            SimpleListPaginator,
            study_key=study_key,
        )

    async def async_list(self, study_key: str) -> List[Job]:
        """
        Asynchronously list all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        return await self._list_impl(
            self._require_async_client(),
            AsyncSimpleListPaginator,
            study_key=study_key,
        )
