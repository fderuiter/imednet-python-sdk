"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, RootModel

from imednet.models.json_base import JsonModel


class Keyword(JsonModel):
    """TODO: Add docstring."""

    pass

    pass


class Record(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    interval_id: Optional[int] = Field(default=None, alias="intervalId")
    form_id: Optional[int] = Field(default=None, alias="formId")
    form_key: Optional[str] = Field(default=None, alias="formKey")
    site_id: Optional[int] = Field(default=None, alias="siteId")
    record_id: Optional[int] = Field(default=None, alias="recordId")
    record_oid: Optional[str] = Field(default=None, alias="recordOid")
    record_type: Optional[str] = Field(default=None, alias="recordType")
    record_status: Optional[str] = Field(default=None, alias="recordStatus")
    deleted: Optional[bool] = Field(default=None, alias="deleted")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")
    subject_id: Optional[int] = Field(default=None, alias="subjectId")
    subject_oid: Optional[str] = Field(default=None, alias="subjectOid")
    subject_key: Optional[str] = Field(default=None, alias="subjectKey")
    visit_id: Optional[int] = Field(default=None, alias="visitId")
    parent_record_id: Optional[int] = Field(default=None, alias="parentRecordId")
    record_data: Optional[Any] = Field(default=None, alias="recordData")

    pass


class RecordJobResponse(JsonModel):
    """TODO: Add docstring."""

    job_id: Optional[str] = Field(default=None, alias="jobId")
    batch_id: Optional[str] = Field(default=None, alias="batchId")
    state: Optional[str] = Field(default=None, alias="state")


    pass


class RecordData(RootModel[Dict[str, Any]]):
    """Arbitrary record data as a dictionary."""

    pass


class BaseRecordRequest(JsonModel):
    """TODO: Add docstring."""

    data: Optional[RecordData] = Field(default=None, alias="data")


    pass


class RegisterSubjectRequest(BaseRecordRequest):
    """Payload for registering (enrolling) a new subject.

    Per the API documentation, registering a subject only requires ``formKey``
    and ``siteName``.  The system assigns the subject identifier upon creation.
    Do **not** include a ``subjectKey`` here — doing so causes the server to
    treat the request as an update and reject it when the key is unknown.
    """

    site_name: str = Field(
        "", alias="siteName", description="Name of the site where the subject is enrolled"
    )

    pass


class UpdateScheduledRecordRequest(BaseRecordRequest):
    """Payload for updating an existing scheduled record."""

    interval_name: str = Field("", alias="intervalName")

    pass


class CreateNewRecordRequest(BaseRecordRequest):
    """Payload for creating a new unscheduled record."""


    pass
