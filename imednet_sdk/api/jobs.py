# API client for interacting with iMednet Jobs endpoints.

from ..models._common import ApiResponse
from ..models.job import JobStatusModel
from ._base import ResourceClient


class JobsClient(ResourceClient):
    """Client for checking the status of background jobs within a study."""

    def get_job_status(
        self, study_key: str, batch_id: str, **kwargs
    ) -> ApiResponse[JobStatusModel]:
        """Gets the status of a specific background job (e.g., record creation).

        Args:
            study_key (str): The key identifying the study.
            batch_id (str): The batch ID identifying the job.
            **kwargs: Optional keyword arguments (currently none defined by API).

        Returns:
            ApiResponse[JobStatusModel]: An API response object containing the job
                                         status and metadata.

        Raises:
            ValueError: If study_key or batch_id is not provided.
        """
        if not study_key:
            raise ValueError("study_key is required.")
        if not batch_id:
            raise ValueError("batch_id is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
        return self._client._get(
            endpoint, params=kwargs, response_model=ApiResponse[JobStatusModel]
        )
