from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Keyword(BaseModel):
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
    def from_json(cls, data: Dict[str, Any]) -> Keyword:
        return cls.model_validate(data)


class Record(BaseModel):
    study_key: str = Field("", alias="studyKey")
    interval_id: int = Field(0, alias="intervalId")
    form_id: int = Field(0, alias="formId")
    form_key: str = Field("", alias="formKey")
    site_id: int = Field(0, alias="siteId")
    record_id: int = Field(0, alias="recordId")
    record_oid: str = Field("", alias="recordOid")
    record_type: str = Field("", alias="recordType")
    record_status: str = Field("", alias="recordStatus")
    deleted: bool = Field(False, alias="deleted")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    subject_id: int = Field(0, alias="subjectId")
    subject_oid: str = Field("", alias="subjectOid")
    subject_key: str = Field("", alias="subjectKey")
    visit_id: int = Field(0, alias="visitId")
    parent_record_id: int = Field(0, alias="parentRecordId")
    keywords: List[Keyword] = Field(default_factory=list, alias="keywords")
    record_data: Dict[str, Any] = Field(default_factory=dict, alias="recordData")

    model_config = ConfigDict(populate_by_name=True)

    # —— Coerce None/"" → defaults for ints
    @field_validator(
        "interval_id",
        "form_id",
        "site_id",
        "record_id",
        "subject_id",
        "visit_id",
        "parent_record_id",
        mode="before",
    )
    def _fill_ints(cls, v):
        if v is None or v == "":
            return 0
        return int(v)

    # —— Coerce None → defaults for strings
    @field_validator(
        "study_key",
        "form_key",
        "record_oid",
        "record_type",
        "record_status",
        "subject_oid",
        "subject_key",
        mode="before",
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

    # —— Parse ISO strings (or default now()) for all datetimes
    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Record:
        return cls.model_validate(data)
