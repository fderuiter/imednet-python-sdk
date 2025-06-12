from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_datetime, parse_str_or_default


class Job(BaseModel):
    job_id: str = Field("", alias="jobId")
    batch_id: str = Field("", alias="batchId")
    state: str = Field("", alias="state")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_started: datetime = Field(default_factory=datetime.now, alias="dateStarted")
    date_finished: datetime = Field(default_factory=datetime.now, alias="dateFinished")

    # Allow instantiation via field names or aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("job_id", "batch_id", "state", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("date_created", "date_started", "date_finished", mode="before")
    def _parse_datetimes(cls, v):
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Job:
        """
        Create a Job instance from a JSON-like dict.
        """
        return cls.model_validate(data)


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
