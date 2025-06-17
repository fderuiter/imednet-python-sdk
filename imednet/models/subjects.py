from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from imednet.utils.validators import (
    parse_bool,
    parse_datetime,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


class SubjectKeyword(BaseModel):
    keyword_name: str = Field("", alias="keywordName")
    keyword_key: str = Field("", alias="keywordKey")
    keyword_id: int = Field(0, alias="keywordId")
    date_added: datetime = Field(default_factory=datetime.now, alias="dateAdded")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("keyword_name", "keyword_key", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("keyword_id", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("date_added", mode="before")
    def _parse_date_added(cls, v):
        return parse_datetime(v)

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

    @field_validator("subject_id", "site_id", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator(
        "study_key", "subject_oid", "subject_key", "subject_status", "site_name", mode="before"
    )
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("keywords", mode="before")
    def _fill_list(cls, v):
        return parse_list_or_default(v)

    @field_validator("deleted", mode="before")
    def parse_bool_field(cls, v):
        return parse_bool(v)

    @field_validator("enrollment_start_date", "date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Subject:
        return cls.model_validate(data)
