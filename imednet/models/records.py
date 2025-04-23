from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Keyword(BaseModel):
    keyword_name: str = Field("", alias="keywordName")
    keyword_key: str = Field("", alias="keywordKey")
    keyword_id: int = Field(0, alias="keywordId")
    date_added: datetime = Field(default_factory=datetime.now, alias="dateAdded")

    # allow population by field names as well as aliases
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
    def from_json(cls, data: Dict[str, Any]) -> Keyword:
        """
        Create a Keyword instance from JSON-like dict.
        """
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
    def from_json(cls, data: Dict[str, Any]) -> Record:
        """
        Create a Record instance from JSON-like dict, including nested Keyword parsing.
        """
        return cls.model_validate(data)
