from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field, model_validator

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Visit(JsonModel):
    """A specific instance of a subject visiting a site (or equivalent event)."""

    visit_id: Optional[str] = Field(None, alias="visitId")

    @model_validator(mode="before")
    @classmethod
    def _clean_empty_dates(cls, data: Any) -> Any:
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


Visit = ModelEngine.get_model('Visit', Visit)
