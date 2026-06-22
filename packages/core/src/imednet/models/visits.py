"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field, model_validator

from imednet.models.json_base import JsonModel


class Visit(JsonModel):
    """TODO: Add docstring."""

    visit_id: Optional[int] = Field(default=None, alias="visitId")
    study_key: Optional[str] = Field(default=None, alias="studyKey")
    interval_id: Optional[int] = Field(default=None, alias="intervalId")
    interval_name: Optional[str] = Field(default=None, alias="intervalName")
    subject_id: Optional[int] = Field(default=None, alias="subjectId")
    subject_key: Optional[str] = Field(default=None, alias="subjectKey")
    start_date: Optional[str] = Field(default=None, alias="startDate")
    end_date: Optional[str] = Field(default=None, alias="endDate")
    due_date: Optional[str] = Field(default=None, alias="dueDate")
    visit_date: Optional[str] = Field(default=None, alias="visitDate")
    deleted: Optional[bool] = Field(default=None, alias="deleted")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")

    @model_validator(mode="before")
    @classmethod
    def _clean_empty_dates(cls, data: Any) -> Any:
        """TODO: Add docstring."""
        if isinstance(data, dict):
            for key in [
                "start_date",
                "end_date",
                "due_date",
                "visit_date",
                "startDate",
                "endDate",
                "dueDate",
                "visitDate",
            ]:
                if data.get(key) == "":
                    data[key] = None
        return data
