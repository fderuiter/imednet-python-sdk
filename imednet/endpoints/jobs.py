"""Endpoint for checking job status in a study."""

from typing import Any, List

from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job, JobStatus


class JobsEndpoint(BaseEndpoint):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    Provides a method to fetch a job by its batch ID.
    """

    PATH = "/api/v1/edc/studies"

    def _validate_job_response(self, data: Any, batch_id: str, study_key: str) -> JobStatus:
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
        endpoint = self._build_path(study_key, "jobs", batch_id)
        response = self._client.get(endpoint)
        return self._validate_job_response(response.json(), batch_id, study_key)

    async def async_get(self, study_key: str, batch_id: str) -> JobStatus:
        """Asynchronous version of :meth:`get`.

        Like the sync variant, it simply issues a request by ``batch_id``
        without any caching.
        """
        client = self._require_async_client()
        endpoint = self._build_path(study_key, "jobs", batch_id)
        response = await client.get(endpoint)
        return self._validate_job_response(response.json(), batch_id, study_key)

    def list(self, study_key: str) -> List[Job]:
        """
        List all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        endpoint = self._build_path(study_key, "jobs")
        response = self._client.get(endpoint)
        return [Job.from_json(item) for item in response.json()]

    async def async_list(self, study_key: str) -> List[Job]:
        """
        Asynchronously list all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        client = self._require_async_client()
        endpoint = self._build_path(study_key, "jobs")
        response = await client.get(endpoint)
        return [Job.from_json(item) for item in response.json()]
