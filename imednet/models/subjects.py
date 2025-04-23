from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectKeyword(BaseModel):
    keyword_name: str = Field("", alias="keywordName")
    keyword_key: str = Field("", alias="keywordKey")
    keyword_id: int = Field(0, alias="keywordId")
    date_added: datetime = Field(default_factory=datetime.now, alias="dateAdded")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("keyword_name", "keyword_key", mode="before")
    def _fill_strs(cls, v):
        if v is None:
            return ""
        return v

    @field_validator("keyword_id", mode="before")
    def _fill_ints(cls, v):
        if v is None or v == "":
            return 0
        return int(v)

    @field_validator("date_added", mode="before")
    def _parse_date_added(cls, v):
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> SubjectKeyword:
        return cls.model_validate(data)


class Subject(BaseModel):
    study_key: str = Field("", alias="studyKey")
    subject_id: int = Field(0, alias="subjectId")
    subject_oid: str = Field("", alias="subjectOid")
    subject_key: str = Field("", alias="subjectKey")
    subject_status: str = Field("", alias="subjectStatus")
    site_id: int = Field(0, alias="siteId")
    site_name: str = Field("", alias="siteName")
    deleted: bool = Field(False, alias="deleted")
    enrollment_start_date: datetime = Field(
        default_factory=datetime.now, alias="enrollmentStartDate"
    )
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    keywords: List[SubjectKeyword] = Field(default_factory=list, alias="keywords")

    model_config = ConfigDict(populate_by_name=True)

    # —— Coerce None/"" → defaults for ints
    @field_validator("subject_id", "site_id", mode="before")
    def _fill_ints(cls, v):
        if v is None or v == "":
            return 0
        return int(v)

    # —— Coerce None → defaults for strings
    @field_validator(
        "study_key", "subject_oid", "subject_key", "subject_status", "site_name", mode="before"
    )
    def _fill_strs(cls, v):
        if v is None:
            return ""
        return v

    # —— Coerce None → empty list
    @field_validator("keywords", mode="before")
    def _fill_list(cls, v):
        if v is None:
            return []
        return v

    # —— Parse ISO strings (or default now()) for datetimes
    @field_validator("enrollment_start_date", "date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Subject:
        return cls.model_validate(data)
