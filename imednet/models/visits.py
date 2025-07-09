from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from imednet.models.json_base import JsonModel


class Visit(JsonModel):
    visit_id: int = Field(0, alias="visitId")
    study_key: str = Field("", alias="studyKey")
    interval_id: int = Field(0, alias="intervalId")
    interval_name: str = Field("", alias="intervalName")
    subject_id: int = Field(0, alias="subjectId")
    subject_key: str = Field("", alias="subjectKey")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    visit_date: Optional[datetime] = Field(None, alias="visitDate")
    visit_date_form: str = Field("", alias="visitDateForm")
    visit_date_question: str = Field("", alias="visitDateQuestion")
    deleted: bool = Field(False, alias="deleted")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    @field_validator(
        "start_date",
        "end_date",
        "due_date",
        "visit_date",
        mode="before",
    )
    def _clean_empty_dates(cls, v):
        if not v:
            return None
        return v

    pass
