from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectKeyword(BaseModel):
    keyword_name: str = Field("", alias="keywordName")
    keyword_key: str = Field("", alias="keywordKey")
    keyword_id: int = Field(0, alias="keywordId")
    date_added: datetime = Field(default_factory=datetime.now, alias="dateAdded")

    # allow instantiation via field names or aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("date_added", mode="before")
    def _parse_date_added(cls, v):
        """
        If missing or empty, default to now(); if string, normalize space to 'T' and parse ISO.
        """
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> SubjectKeyword:
        """
        Create a SubjectKeyword instance from JSON-like dict.
        """
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

    @field_validator("enrollment_start_date", "date_created", "date_modified", mode="before")
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
    def from_json(cls, data: Dict[str, Any]) -> Subject:
        """
        Create a Subject instance from JSON-like dict, including nested keywords.
        """
        return cls.model_validate(data)
