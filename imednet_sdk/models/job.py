"""Job status models for tracking asynchronous operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ._common import ErrorDetail


class JobStatusModel(BaseModel):
    """Model representing the status of an asynchronous job."""

    model_config = ConfigDict(populate_by_name=True)

    jobId: str = Field(..., description="Unique identifier for the job")
    batchId: Optional[str] = Field(
        None, description="Batch ID associated with the submitted records"
    )
    state: str = Field(
        ..., description="Current status of the job (e.g., created, processing, completed, failed)"
    )
    dateCreated: datetime = Field(
        ..., description="Timestamp when the job was created"
    )  # Add dateCreated
    dateModified: Optional[datetime] = Field(
        None, description="Timestamp when the job was last modified"
    )
    # Add other fields based on docs/reference/jobs.md if needed, e.g., progress, resultUrl
    progress: Optional[int] = Field(None, ge=0, le=100, description="Job progress percentage")
    resultUrl: Optional[str] = Field(None, description="URL to retrieve job results if applicable")
    error: Optional[ErrorDetail] = Field(None, description="Error details if the job failed")
