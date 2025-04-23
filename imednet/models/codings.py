from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Coding(BaseModel):
    study_key: str = Field("", alias="studyKey")
    site_name: str = Field("", alias="siteName")
    site_id: int = Field(0, alias="siteId")
    subject_id: int = Field(0, alias="subjectId")
    subject_key: str = Field("", alias="subjectKey")
    form_id: int = Field(0, alias="formId")
    form_name: str = Field("", alias="formName")
    form_key: str = Field("", alias="formKey")
    revision: int = Field(0, alias="revision")
    record_id: int = Field(0, alias="recordId")
    variable: str = Field("", alias="variable")
    value: str = Field("", alias="value")
    coding_id: int = Field(0, alias="codingId")
    code: str = Field("", alias="code")
    coded_by: str = Field("", alias="codedBy")
    reason: str = Field("", alias="reason")
    dictionary_name: str = Field("", alias="dictionaryName")
    dictionary_version: str = Field("", alias="dictionaryVersion")
    date_coded: datetime = Field(default_factory=datetime.now, alias="dateCoded")

    # allow population by field names as well as aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("date_coded", mode="before")
    def _parse_date_coded(cls, v: str | datetime) -> datetime:
        """
        If missing or falsy, default to now(); if it's a string, normalize
        any space to 'T' and parse ISO format.
        """
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Coding:
        """
        Create a Coding instance from a JSON-like dict.
        """
        return cls.model_validate(data)
