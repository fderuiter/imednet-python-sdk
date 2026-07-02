"""Record (eCRF instance) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, RootModel

from imednet.models.engine import ModelEngine
from imednet.models.base import ImednetBaseModel

class Keyword(ImednetBaseModel):
    """A keyword or tag associated with a record."""

    pass

    pass

class Record(ImednetBaseModel):
    """A data record for a subject, form, and visit."""

    pass

    study_key: Optional[str]
    interval_id: Optional[int]
    form_id: Optional[int]
    form_key: Optional[str]
    site_id: Optional[int]
    record_id: Optional[int]
    record_oid: Optional[str]
    record_type: Optional[str]
    record_status: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    subject_id: Optional[int]
    subject_oid: Optional[str]
    subject_key: Optional[str]
    visit_id: Optional[int]
    parent_record_id: Optional[int]
    record_data: Any

class RecordJobResponse(ImednetBaseModel):
    """Response for a record-related job (batch operations, etc)."""

    job_id: str = Field("", alias="jobId")
    batch_id: str = Field("", alias="batchId")
    state: str = Field("", alias="state")

    pass

class RecordData(RootModel[Dict[str, Any]]):
    """Arbitrary record data as a dictionary."""

    pass

class BaseRecordRequest(ImednetBaseModel):
    """Base class for record creation/update requests."""

    form_key: str = Field("", alias="formKey")
    data: RecordData = Field(default_factory=lambda: RecordData({}), alias="data")

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

    subject_key: str = Field("", alias="subjectKey")
    interval_name: str = Field("", alias="intervalName")

    pass

class CreateNewRecordRequest(BaseRecordRequest):
    """Payload for creating a new unscheduled record."""

    subject_key: str = Field("", alias="subjectKey")

    pass
