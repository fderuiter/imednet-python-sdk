from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_bool, parse_datetime, parse_int_or_default, parse_str_or_default


class RecordRevision(BaseModel):
    study_key: str = Field("", alias="studyKey")
    record_revision_id: int = Field(0, alias="recordRevisionId")
    record_id: int = Field(0, alias="recordId")
    record_oid: str = Field("", alias="recordOid")
    record_revision: int = Field(0, alias="recordRevision")
    data_revision: int = Field(0, alias="dataRevision")
    record_status: str = Field("", alias="recordStatus")
    subject_id: int = Field(0, alias="subjectId")
    subject_oid: str = Field("", alias="subjectOid")
    subject_key: str = Field("", alias="subjectKey")
    site_id: int = Field(0, alias="siteId")
    form_key: str = Field("", alias="formKey")
    interval_id: int = Field(0, alias="intervalId")
    role: str = Field("", alias="role")
    user: str = Field("", alias="user")
    reason_for_change: str = Field("", alias="reasonForChange")
    deleted: bool = Field(False, alias="deleted")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "record_revision_id",
        "record_id",
        "record_revision",
        "data_revision",
        "subject_id",
        "site_id",
        "interval_id",
        mode="before",
    )
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator(
        "study_key",
        "record_oid",
        "record_status",
        "subject_oid",
        "subject_key",
        "form_key",
        "role",
        "user",
        "reason_for_change",
        mode="before",
    )
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("deleted", mode="before")
    def _parse_deleted(cls, v):
        return parse_bool(v)

    @field_validator("date_created", mode="before")
    def _parse_date_created(cls, v):
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> RecordRevision:
        """
        Create a RecordRevision instance from JSON-like dict.
        """
        return cls.model_validate(data)
