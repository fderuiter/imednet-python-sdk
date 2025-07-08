from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class RecordRevision(JsonModel):
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

    pass
