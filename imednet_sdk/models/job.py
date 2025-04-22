"""Pydantic models related to iMednet asynchronous Jobs.

This module defines the Pydantic model `JobStatusModel` which represents the
structure of job status data retrieved from the iMednet API, typically via the
`/jobs` endpoint. Jobs are used for tracking the progress of asynchronous
operations like bulk record creation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ._common import ErrorDetail


class JobStatusModel(BaseModel):
    """Represents the status and details of an asynchronous background job in iMednet."""

    model_config = ConfigDict(populate_by_name=True)

    jobId: str = Field(..., description="Unique identifier for the job")
    # batchId is often the primary key used in requests/responses per docs
    # Making it string as per test failure, assuming it's always present in responses
    batchId: str = Field(..., description="Batch ID associated with the submitted records")
    state: str = Field(
        ..., description="Current status of the job (e.g., created, processing, completed, failed)"
    )
    # Make dateCreated required (remove Optional and default=None if they existed)
    dateCreated: datetime = Field(..., description="Timestamp when the job was created")
    # Add optional dateStarted and dateFinished based on test failure and docs
    dateStarted: Optional[datetime] = Field(
        None, description="Timestamp when the job started processing"
    )
    dateFinished: Optional[datetime] = Field(
        None, description="Timestamp when the job finished processing"
    )
