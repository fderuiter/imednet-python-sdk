from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Study(JsonModel):
    """Represents a clinical study and its metadata."""

    sponsor_key: str = Field("", alias="sponsorKey")
    study_key: str = Field("", alias="studyKey")
    study_id: int = Field(0, alias="studyId")
    study_name: str = Field("", alias="studyName")
    study_description: str = Field("", alias="studyDescription")
    study_type: str = Field("", alias="studyType")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    pass
