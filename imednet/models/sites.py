from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Site(BaseModel):
    study_key: str = Field("", alias="studyKey")
    site_id: int = Field(0, alias="siteId")
    site_name: str = Field("", alias="siteName")
    site_enrollment_status: str = Field("", alias="siteEnrollmentStatus")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    # allow population by field names as well as aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        """
        If missing or empty, default to now(); if string, normalize space to 'T' and parse ISO.
        """
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Site:
        """
        Create a Site instance from JSON-like dict.
        """
        return cls.model_validate(data)
