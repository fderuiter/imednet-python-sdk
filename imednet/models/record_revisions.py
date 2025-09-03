from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class RecordRevision(JsonModel):
    """Represents a single revision of a record in the audit trail."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    record_revision_id: int = Field(
        0, alias="recordRevisionId", description="The ID of the record revision."
    )
    record_id: int = Field(0, alias="recordId", description="The ID of the record.")
    record_oid: str = Field("", alias="recordOid", description="The OID of the record.")
    record_revision: int = Field(
        0, alias="recordRevision", description="The revision number of the record."
    )
    data_revision: int = Field(0, alias="dataRevision", description="The data revision number.")
    record_status: str = Field("", alias="recordStatus", description="The status of the record.")
    subject_id: int = Field(0, alias="subjectId", description="The ID of the subject.")
    subject_oid: str = Field("", alias="subjectOid", description="The OID of the subject.")
    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
    site_id: int = Field(0, alias="siteId", description="The ID of the site.")
    form_key: str = Field("", alias="formKey", description="The key of the form.")
    interval_id: int = Field(0, alias="intervalId", description="The ID of the interval.")
    role: str = Field("", alias="role", description="The role of the user who made the change.")
    user: str = Field("", alias="user", description="The user who made the change.")
    reason_for_change: str = Field(
        "", alias="reasonForChange", description="The reason for the change."
    )
    deleted: bool = Field(
        False, alias="deleted", description="Indicates if the record was deleted."
    )
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the revision was created.",
    )
