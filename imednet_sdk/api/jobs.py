"""API client for interacting with the iMednet Jobs endpoints.

This module provides the `JobsClient` class for checking the status of
asynchronous background jobs initiated via the iMednet API.
"""

from ..models.job import JobStatusModel
from ._base import ResourceClient


class JobsClient(ResourceClient):
    """Provides methods for checking the status of iMednet background jobs.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/jobs`.
    It is accessed via the `imednet_sdk.client.ImednetClient.jobs` property.
    Background jobs are often initiated by other API calls, such as bulk record creation.
    """

    def get_job_status(self, study_key: str, batch_id: str) -> JobStatusModel:
        """Retrieves the status of a specific background job.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/jobs/{batchId}` endpoint.
        This is used to check the progress and outcome of asynchronous operations.

        Args:
            study_key: The unique identifier for the study where the job was initiated.
            batch_id: The unique identifier for the batch job, typically returned
                      by the API call that initiated the job.

        Returns:
            A `JobStatusModel` instance containing details about the job's status,
            progress, and any results or errors.

        Raises:
            ValueError: If `study_key` or `batch_id` are empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, job not found).
        """
        if not study_key:
            raise ValueError("study_key is required.")
        if not batch_id:
            raise ValueError("batch_id is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
        # Use self._get instead of self._client._get
        return self._get(endpoint, response_model=JobStatusModel)
