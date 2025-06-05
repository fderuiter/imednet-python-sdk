"""Representation of asynchronous job results."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_datetime, parse_str_or_default


class Job(BaseModel):
    """
    Represents a job entity with associated metadata and state.
    Attributes:
        job_id (str): Unique identifier for the job.
        batch_id (str): Identifier for the batch this job belongs to.
        state (str): Current state of the job.
        date_created (datetime): Timestamp when the job was created.
        date_started (datetime): Timestamp when the job started processing.
        date_finished (datetime): Timestamp when the job finished processing.
    Methods:
        from_json(data: Dict[str, Any]) -> Job:
            Creates a Job instance from a JSON-like dictionary.
    Validators:
        _fill_strs: Ensures string fields are properly parsed or defaulted.
        _parse_datetimes: Parses and validates datetime fields.
    """

    job_id: str = Field("", alias="jobId")
    batch_id: str = Field("", alias="batchId")
    state: str = Field("", alias="state")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_started: datetime = Field(default_factory=datetime.now, alias="dateStarted")
    date_finished: datetime = Field(default_factory=datetime.now, alias="dateFinished")

    # Allow instantiation via field names or aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("job_id", "batch_id", "state", mode="before")
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("date_created", "date_started", "date_finished", mode="before")
    def _parse_datetimes(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Job":
        """
        Create a Job instance from a JSON-like dict.
        """
        return cls.model_validate(data)
