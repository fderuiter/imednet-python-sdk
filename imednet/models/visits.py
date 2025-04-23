from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Visit(BaseModel):
    visit_id: int = Field(0, alias="visitId")
    study_key: str = Field("", alias="studyKey")
    interval_id: int = Field(0, alias="intervalId")
    interval_name: str = Field("", alias="intervalName")
    subject_id: int = Field(0, alias="subjectId")
    subject_key: str = Field("", alias="subjectKey")
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
    due_date: Optional[date] = Field(None, alias="dueDate")
    visit_date: Optional[date] = Field(None, alias="visitDate")
    visit_date_form: str = Field("", alias="visitDateForm")
    visit_date_question: str = Field("", alias="visitDateQuestion")
    deleted: bool = Field(False, alias="deleted")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    # Ensure aliases are recognized on instantiation
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("start_date", "end_date", "due_date", "visit_date", mode="before")
    def _clean_empty_dates(cls, v):
        """
        Treat missing or empty-string dates as None; let Pydantic parse valid ISO date strings.
        """
        if not v:
            return None
        return v

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        """
        If no timestamp is provided or it's an empty string, default to now().
        If it's a string, normalize any space to 'T' and parse.
        """
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @field_validator("deleted", mode="before")
    def _normalize_deleted(cls, v):
        """
        Ensure that any falsy value—None, empty string, etc.—becomes False.
        """
        if not v:
            return False
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Visit:
        """
        Create a Visit instance from a JSON-like dict, honoring all the same parsing rules
        as the original dataclass.from_json.
        """
        return cls.model_validate(data)
