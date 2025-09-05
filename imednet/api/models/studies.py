from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .json_base import JsonModel


class Study(JsonModel):
    """Represents a clinical study and its metadata."""

    sponsor_key: str = Field("", alias="sponsorKey", description="The key of the study sponsor.")
    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    study_id: int = Field(0, alias="studyId", description="The ID of the study.")
    study_name: str = Field("", alias="studyName", description="The name of the study.")
    study_description: str = Field(
        "", alias="studyDescription", description="The description of the study."
    )
    study_type: str = Field("", alias="studyType", description="The type of the study.")
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the study was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the study was last modified.",
    )
