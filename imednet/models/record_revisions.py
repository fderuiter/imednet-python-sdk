"""Models describing revisions of records in the audit trail."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_bool, parse_datetime, parse_int_or_default, parse_str_or_default


class RecordRevision(BaseModel):
    """
    A Pydantic model representing record revision data in the iMedNet system.
    This class models record revisions with properties such as study key, record IDs,
    revision numbers, statuses, subject information, site details, and audit trail
    information including user, role, and reason for change.
    Attributes:
        study_key (str): The unique identifier for the study.
        record_revision_id (int): The identifier for the specific record revision.
        record_id (int): The identifier for the record.
        record_oid (str): The object identifier for the record.
        record_revision (int): The revision number for the record.
        data_revision (int): The revision number for the data.
        record_status (str): The current status of the record (e.g., "Complete", "Incomplete").
        subject_id (int): The identifier for the subject.
        subject_oid (str): The object identifier for the subject.
        subject_key (str): The unique key for the subject.
        site_id (int): The identifier for the site.
        form_key (str): The key identifying the form.
        interval_id (int): The identifier for the interval.
        role (str): The role of the user who created or modified the revision.
        user (str): The username of the person who created or modified the revision.
        reason_for_change (str): Documentation of why the change was made.
        deleted (bool): Flag indicating if the record revision is deleted.
        date_created (datetime): The timestamp when the revision was created.
    Methods:
        from_json: Creates a RecordRevision instance from a JSON-like dictionary.
    """

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
    def _fill_ints(cls, v: Any) -> int:
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
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("deleted", mode="before")
    def _parse_deleted(cls, v: Any) -> bool:
        return parse_bool(v)

    @field_validator("date_created", mode="before")
    def _parse_date_created(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "RecordRevision":
        """
        Create a RecordRevision instance from JSON-like dict.
        """
        return cls.model_validate(data)
