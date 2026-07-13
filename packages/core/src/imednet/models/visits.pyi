"""Models for subject visits and study events."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field, model_validator

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

class Visit(ImednetBaseModel):
    """A specific instance of a subject visiting a site (or equivalent event)."""

    @model_validator(mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _clean_empty_dates(cls, data: Any) -> Any:
        """Coerce empty strings in date fields to None before validation."""
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

    visit_id: Optional[int]
    study_key: Optional[str]
    interval_id: Optional[int]
    interval_name: Optional[str]
    subject_id: Optional[int]
    subject_key: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    due_date: Optional[str]
    visit_date: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    visit_date_form: Any
    visit_date_question: Any
