"""Endpoint for checking job status in a study."""

from typing import List

from imednet.core.parsing import get_model_parser
from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job, JobStatus


class JobsEndpoint(BaseEndpoint):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    This endpoint provides methods to fetch individual job status by batch ID
    and list all jobs for a study.
    """

    PATH = "/api/v1/edc/studies"

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
        endpoint = self._build_path(study_key, "jobs", batch_id)
        response = self._client.get(endpoint)
        data = response.json()
        if not data:
            raise ValueError(f"Job {batch_id} not found in study {study_key}")
        parser = get_model_parser(JobStatus)
        return parser(data)

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
        endpoint = self._build_path(study_key, "jobs", batch_id)
        response = await client.get(endpoint)
        data = response.json()
        if not data:
            raise ValueError(f"Job {batch_id} not found in study {study_key}")
        parser = get_model_parser(JobStatus)
        return parser(data)

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
        parser = get_model_parser(Job)
        return [parser(item) for item in response.json()]

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
        parser = get_model_parser(Job)
        return [parser(item) for item in response.json()]
