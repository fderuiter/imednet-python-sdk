"""Client for interacting with the Jobs endpoint."""

# API client for interacting with iMednet Jobs endpoints.

from ..models.job import JobStatusModel
from ._base import ResourceClient


class JobsClient(ResourceClient):
    """Client for checking the status of background jobs within a study."""

    def get_job_status(self, study_key: str, batch_id: str) -> JobStatusModel:
        """
        Gets the status of a specific background job (e.g., record creation).

        Corresponds to GET /api/v1/edc/studies/{studyKey}/jobs/{batchId}.

        Args:
            study_key: The key identifying the study.
            batch_id: The ID of the batch job.

        Returns:
            A JobStatus object containing the status details.

        Raises:
            ImednetAPIError: If the API request fails.
        """
        if not study_key:
            raise ValueError("study_key is required.")
        if not batch_id:
            raise ValueError("batch_id is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
        return self._client._get(endpoint, response_model=JobStatusModel)
