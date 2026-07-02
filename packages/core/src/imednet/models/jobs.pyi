"""Job and background operation models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel



class Job(JsonModel):
    job_id: Optional[str]
    batch_id: Optional[str]
    state: Optional[str]
    date_created: Any
    date_finished: Any
    date_started: Any


class JobStatus(Job):
    job_id: Optional[str]
    batch_id: Optional[str]
    state: Optional[str]
    date_created: Optional[str]
    date_started: Optional[str]
    date_finished: Optional[str]
    progress: Optional[int]
    result_url: Optional[str]

