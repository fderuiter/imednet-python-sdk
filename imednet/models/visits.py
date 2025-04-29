from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_bool, parse_datetime, parse_int_or_default, parse_str_or_default


class Visit(BaseModel):
    """
    Represents a visit in a clinical study.
    The Visit class models a subject's visit within a clinical study,
    storing information about when the visit occurred, when it was scheduled,
    and the associated study and subject details.
    Attributes:
        visit_id (int): Unique identifier for the visit.
        study_key (str): Key identifying the study to which this visit belongs.
        interval_id (int): Identifier for the interval associated with this visit.
        interval_name (str): Name of the interval associated with this visit.
        subject_id (int): Identifier for the subject who attended the visit.
        subject_key (str): Key identifying the subject who attended the visit.
        start_date (Optional[datetime]): The date and time when the visit started.
        end_date (Optional[datetime]): The date and time when the visit ended.
        due_date (Optional[datetime]): The date and time when the visit was scheduled.
        visit_date (Optional[datetime]): The date and time when the visit actually occurred.
        visit_date_form (str): Form identifier associated with the visit date.
        visit_date_question (str): Question identifier associated with the visit date.
        deleted (bool): Flag indicating whether this visit has been marked as deleted.
        date_created (datetime): The date and time when this visit record was created.
        date_modified (datetime): The date and time when this visit record was last modified.
    """

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

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "study_key",
        "interval_name",
        "subject_key",
        "visit_date_form",
        "visit_date_question",
        mode="before",
    )
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("visit_id", "interval_id", "subject_id", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("start_date", "end_date", "due_date", "visit_date", mode="before")
    def _clean_empty_dates(cls, v):
        if not v:
            return None
        return v

    @field_validator("deleted", mode="before")
    def parse_bool_field(cls, v):
        return parse_bool(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Visit:
        """
        Create a Visit instance from a JSON-like dict, honoring all the same parsing rules
        as the original dataclass.from_json.
        """
        return cls.model_validate(data)
