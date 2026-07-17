"""Models for subject visits and study events."""

from __future__ import annotations

from typing import Any

from pydantic import model_validator

from imednet.models.base import ImednetBaseModel

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

    visit_id: int | None
    study_key: str | None
    interval_id: int | None
    interval_name: str | None
    subject_id: int | None
    subject_key: str | None
    start_date: str | None
    end_date: str | None
    due_date: str | None
    visit_date: str | None
    deleted: bool | None
    date_created: str | None
    date_modified: str | None
    visit_date_form: Any
    visit_date_question: Any
