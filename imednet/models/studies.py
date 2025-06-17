from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from imednet.utils.validators import (
    parse_datetime,
    parse_int_or_default,
    parse_str_or_default,
)


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

    @field_validator(
        "sponsor_key", "study_key", "study_name", "study_description", "study_type", mode="before"
    )
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("study_id", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_dates(cls, v):
        return parse_datetime(v)
