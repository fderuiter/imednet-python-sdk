from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_int_or_default, parse_str_or_default


class Study(BaseModel):
    sponsor_key: str = Field("", alias="sponsorKey")
    study_key: str = Field("", alias="studyKey")
    study_id: int = Field(0, alias="studyId")
    study_name: str = Field("", alias="studyName")
    study_description: str | None = Field(None, alias="studyDescription")
    study_type: str = Field("", alias="studyType")
    date_created: str = Field("", alias="dateCreated")
    date_modified: str = Field("", alias="dateModified")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "sponsor_key",
        "study_key",
        "study_name",
        "study_type",
        "date_created",
        "date_modified",
        mode="before",
    )
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("study_description", mode="before")
    def _fill_optional_str(cls, v: Any) -> str | None:
        if v is None:
            return None
        return parse_str_or_default(v)

    @field_validator("study_id", mode="before")
    def _fill_ints(cls, v: Any) -> int:
        return parse_int_or_default(v)
