from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from imednet.models.json_base import JsonModel


class Job(JsonModel):
    """Represents an asynchronous background job."""

    job_id: str = Field("", alias="jobId")
    batch_id: str = Field("", alias="batchId")
    state: str = Field("", alias="state")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_started: datetime = Field(default_factory=datetime.now, alias="dateStarted")
    date_finished: datetime = Field(default_factory=datetime.now, alias="dateFinished")

    @property
    def is_terminal(self) -> bool:
        """Checks if the job has reached a final state (Success/Failed/Cancelled)."""
        return self.state.upper() in {"COMPLETED", "SUCCESS", "FAILED", "CANCELLED"}

    @property
    def is_successful(self) -> bool:
        """Checks if the job completed successfully."""
        return self.state.upper() in {"COMPLETED", "SUCCESS"}

    @property
    def is_failed(self) -> bool:
        """Checks if the job failed or was cancelled."""
        return self.state.upper() in {"FAILED", "CANCELLED"}


class JobStatus(Job):
    """Extended job information returned when polling."""

    progress: int = Field(0, alias="progress")
    result_url: str = Field("", alias="resultUrl")

    @field_validator("progress", mode="before")
    def _parse_progress(cls, v: Any) -> int:
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0
