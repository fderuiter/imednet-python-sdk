from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from imednet.models.base import Metadata, Pagination


class Study(BaseModel):
    sponsor_key: str = Field("", alias="sponsorKey")
    study_key: str = Field("", alias="studyKey")
    study_id: int = Field(0, alias="studyId")
    study_name: str = Field("", alias="studyName")
    study_description: str = Field("", alias="studyDescription")
    study_type: str = Field("", alias="studyType")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_dates(cls, v):
        """
        Parse or default study creation/modification dates.
        """
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v


class StudiesResponse(BaseModel):
    metadata: Metadata
    pagination: Pagination
    data: List[Study]

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> StudiesResponse:
        """
        Create a StudiesResponse instance from JSON-like dict.
        """
        return cls.model_validate(data)
