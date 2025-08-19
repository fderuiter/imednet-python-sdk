from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import Field, RootModel

from imednet.models.json_base import JsonModel


class Keyword(JsonModel):
    """A keyword or tag associated with a record."""

    keyword_name: str = Field("", alias="keywordName")
    keyword_key: str = Field("", alias="keywordKey")
    keyword_id: int = Field(0, alias="keywordId")
    date_added: datetime = Field(default_factory=datetime.now, alias="dateAdded")

    pass


class Record(JsonModel):
    """A data record for a subject, form, and visit."""

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

    pass


class RecordJobResponse(JsonModel):
    """Response for a record-related job (batch operations, etc)."""

    job_id: str = Field("", alias="jobId")
    batch_id: str = Field("", alias="batchId")
    state: str = Field("", alias="state")

    pass


class RecordData(RootModel[Dict[str, Any]]):
    """Arbitrary record data as a dictionary."""

    pass


class BaseRecordRequest(JsonModel):
    """Base class for record creation/update requests."""

    form_key: str = Field("", alias="formKey")
    data: RecordData = Field(default_factory=lambda: RecordData({}), alias="data")

    pass


class RegisterSubjectRequest(BaseRecordRequest):
    site_name: str = Field(
        "", alias="siteName", description="Name of the site where the subject is enrolled"
    )
    subject_key: str = Field(
        "", alias="subjectKey", description="Unique identifier for the subject"
    )

    pass


class UpdateScheduledRecordRequest(BaseRecordRequest):
    subject_key: str = Field("", alias="subjectKey")
    interval_name: str = Field("", alias="intervalName")

    pass


class CreateNewRecordRequest(BaseRecordRequest):
    subject_key: str = Field("", alias="subjectKey")

    pass
