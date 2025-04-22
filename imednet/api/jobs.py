"""
Pydantic model and API client for iMednet “jobs”.

This module provides:

- `JobStatusModel`: a Pydantic model representing the status of asynchronous background jobs.
- `JobsClient`: an API client for the `/api/v1/edc/studies/{study_key}/jobs` endpoints.
"""

from datetime import datetime
from typing import Optional, cast

from pydantic import BaseModel, ConfigDict, Field

from ._base import ResourceClient


class JobStatusModel(BaseModel):
    """Represents the status and details of an asynchronous background job in iMednet."""

    model_config = ConfigDict(populate_by_name=True)

    jobId: str = Field(..., description="Unique identifier for the job")
    batchId: str = Field(..., description="Batch ID associated with the submitted records")
    state: str = Field(
        ..., description="Current status of the job (e.g., created, processing, completed, failed)"
    )
    dateCreated: datetime = Field(..., description="Timestamp when the job was created")
    dateStarted: Optional[datetime] = Field(
        None, description="Timestamp when the job started processing"
    )
    dateFinished: Optional[datetime] = Field(
        None, description="Timestamp when the job finished processing"
    )


class JobsClient(ResourceClient):
    """Provides methods for checking the status of iMednet background jobs."""

    def get_job_status(self, study_key: str, batch_id: str) -> JobStatusModel:
        """Retrieves the status of a specific background job.

        GET /api/v1/edc/studies/{studyKey}/jobs/{batchId}

        Args:
            study_key: The unique identifier for the study where the job was initiated.
            batch_id: The unique identifier for the batch job.

        Returns:
            A `JobStatusModel` instance with details about the job's status.

        Raises:
            ValueError: If `study_key` or `batch_id` are empty.
            ImednetSdkException: If the API request fails.
        """
        if not study_key:
            raise ValueError("study_key is required.")
        if not batch_id:
            raise ValueError("batch_id is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
        # Cast the result to the expected type
        response = cast(JobStatusModel, self._get(endpoint, response_model=JobStatusModel))
        return response
