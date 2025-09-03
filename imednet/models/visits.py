from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from imednet.models.json_base import JsonModel


class Visit(JsonModel):
    """Represents a subject's visit for a specific interval."""

    visit_id: int = Field(0, alias="visitId", description="The ID of the visit.")
    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    interval_id: int = Field(0, alias="intervalId", description="The ID of the interval.")
    interval_name: str = Field("", alias="intervalName", description="The name of the interval.")
    subject_id: int = Field(0, alias="subjectId", description="The ID of the subject.")
    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
    start_date: Optional[datetime] = Field(
        None, alias="startDate", description="The start date of the visit window."
    )
    end_date: Optional[datetime] = Field(
        None, alias="endDate", description="The end date of the visit window."
    )
    due_date: Optional[datetime] = Field(
        None, alias="dueDate", description="The due date of the visit."
    )
    visit_date: Optional[datetime] = Field(
        None, alias="visitDate", description="The actual date of the visit."
    )
    visit_date_form: str = Field(
        "", alias="visitDateForm", description="The form used to determine the visit date."
    )
    visit_date_question: str = Field(
        "", alias="visitDateQuestion", description="The question used to determine the visit date."
    )
    deleted: bool = Field(False, alias="deleted", description="Indicates if the visit is deleted.")
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the visit was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the visit was last modified.",
    )

    @field_validator(
        "start_date",
        "end_date",
        "due_date",
        "visit_date",
        mode="before",
    )
    def _clean_empty_dates(cls, v):
        """Ensure that empty date strings are parsed as None."""
        if not v:
            return None
        return v
