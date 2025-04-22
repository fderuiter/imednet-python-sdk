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
    """Represents the status and details of an asynchronous background job in iMednet.

    This model is returned when initiating an asynchronous operation (like creating
    records) and when querying the status of an existing job via the `/jobs` endpoint.

    Attributes:
        jobId: Unique identifier assigned by iMednet to this specific job instance.
               (Note: API docs often use `batchId` interchangeably or primarily).
        batchId: The batch identifier associated with the submitted request, often
                 used to query the job status. May be the primary ID returned.
        state: A string indicating the current state of the job (e.g., "created",
               "processing", "completed", "failed").
        dateCreated: The date and time when the job was initially created.
        dateModified: The date and time when the job status was last updated.
        progress: An optional integer (0-100) indicating the percentage completion
                  of the job.
        resultUrl: An optional URL where detailed results or logs for the job
                   can be retrieved, if applicable.
        error: An optional `ErrorDetail` object containing information if the job
               encountered an error during processing.
    """

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
