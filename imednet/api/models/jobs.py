from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from .json_base import JsonModel


class Job(JsonModel):
    """Represents a job in the system."""

    job_id: str = Field("", alias="jobId", description="The ID of the job.")
    batch_id: str = Field("", alias="batchId", description="The batch ID of the job.")
    state: str = Field("", alias="state", description="The current state of the job.")
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the job was created.",
    )
    date_started: datetime = Field(
        default_factory=datetime.now,
        alias="dateStarted",
        description="The date the job was started.",
    )
    date_finished: datetime = Field(
        default_factory=datetime.now,
        alias="dateFinished",
        description="The date the job was finished.",
    )


class JobStatus(Job):
    """Represents the detailed status of a job, including progress and results."""

    progress: int = Field(
        0, alias="progress", description="The progress of the job as a percentage."
    )
    result_url: str = Field(
        "",
        alias="resultUrl",
        description="The URL where the job result can be downloaded.",
    )

    @field_validator("progress", mode="before")
    def _parse_progress(cls, v: Any) -> int:
        """Parse the progress value, defaulting to 0 on failure."""
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0
