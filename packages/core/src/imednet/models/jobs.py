from __future__ import annotations

from imednet.models.engine import ModelEngine

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from imednet.models.json_base import JsonModel


class Job(JsonModel):
    """Represents an asynchronous background job."""


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


Job = ModelEngine.get_model('Job', Job)

class JobStatus(Job):
    """Extended job information returned when polling."""


    @field_validator("progress", mode="before", check_fields=False)
    def _parse_progress(cls, v: Any) -> int:
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0
JobStatus = ModelEngine.get_model('JobStatus', JobStatus)

