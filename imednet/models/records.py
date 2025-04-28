from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from .validators import (
    parse_bool,
    parse_datetime,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


class Keyword(BaseModel):
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
        return parse_int_or_default(v)

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
        return parse_str_or_default(v)

    @field_validator("keywords", mode="before")
    def _fill_list(cls, v):
        return parse_list_or_default(v)

    @field_validator("deleted", mode="before")
    def parse_bool_field(cls, v):
        return parse_bool(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Record:
        return cls.model_validate(data)


class RecordJobResponse(BaseModel):
    job_id: str = Field("", alias="jobId")
    batch_id: str = Field("", alias="batchId")
    state: str = Field("", alias="state")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("job_id", "batch_id", "state", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> RecordJobResponse:
        return cls.model_validate(data)


class RecordData(RootModel[Dict[str, Any]]):
    pass


class BaseRecordRequest(BaseModel):
    form_key: str = Field("", alias="formKey")
    data: RecordData = Field(default_factory=lambda: RecordData({}), alias="data")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("form_key", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)


class RegisterSubjectRequest(BaseRecordRequest):
    site_name: str = Field("", alias="siteName")

    @field_validator("site_name", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)


class UpdateScheduledRecordRequest(BaseRecordRequest):
    subject_key: str = Field("", alias="subjectKey")
    interval_name: str = Field("", alias="intervalName")

    @field_validator("subject_key", "interval_name", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)


class CreateNewRecordRequest(BaseRecordRequest):
    subject_key: str = Field("", alias="subjectKey")

    @field_validator("subject_key", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)
