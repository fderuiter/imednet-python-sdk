"""Job status models for tracking asynchronous operations."""

from datetime import datetime
from typing import Optional  # Import Optional

from pydantic import BaseModel, Field


class JobStatusModel(BaseModel):
    """Model for job status information."""

    jobId: str = Field(..., description="Unique identifier for the job")
    batchId: str = Field(..., description="Batch ID linked to the submitted job")
    state: str = Field(..., description="Current state of the job")
    dateCreated: datetime = Field(..., description="Timestamp when the job was created")
    dateStarted: Optional[datetime] = Field(
        None, description="Timestamp when the job started processing"
    )  # Allow None
    dateFinished: Optional[datetime] = Field(
        None, description="Timestamp when the job completed processing"
    )  # Allow None
