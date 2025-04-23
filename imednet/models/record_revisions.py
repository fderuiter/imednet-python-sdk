from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    # —— Coerce None/"" → defaults for all integer fields
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
        if v is None or v == "":
            return 0
        return int(v)

    # —— Coerce None → defaults for all string fields
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
        if v is None:
            return ""
        return v

    # —— Ensure 'deleted' isn’t None
    @field_validator("deleted", mode="before")
    def _fill_deleted(cls, v):
        if v is None:
            return False
        return bool(v)

    # —— Parse ISO strings (or default now()) for date_created
    @field_validator("date_created", mode="before")
    def _parse_date_created(cls, v):
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> RecordRevision:
        """
        Create a RecordRevision instance from JSON-like dict.
        """
        return cls.model_validate(data)
