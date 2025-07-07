"""Endpoint for checking job status in a study."""

import inspect
from typing import Any

from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import JobStatus


class JobsEndpoint(BaseEndpoint):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    Provides a method to fetch a job by its batch ID.
    """

    PATH = "/api/v1/edc/studies"

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
