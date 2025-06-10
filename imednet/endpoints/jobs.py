"""Endpoint for checking job status in a study."""

from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job


class JobsEndpoint(BaseEndpoint):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    Provides a method to fetch a job by its batch ID.
    """

    path = "/api/v1/edc/studies"

    def get(self, study_key: str, batch_id: str) -> Job:
        """
        Get a specific job by batch ID.

        Args:
            study_key: Study identifier
            batch_id: Batch ID of the job

        Returns:
            Job object with current state and timestamps
        """
        # Construct the endpoint path
        endpoint = self._build_path(study_key, "jobs", batch_id)
        # Execute the request
        response = self._client.get(endpoint)
        data = response.json()
        if not data:
            raise ValueError(f"Job {batch_id} not found in study {study_key}")
        return Job.from_json(data)


__all__ = ["JobsEndpoint"]
