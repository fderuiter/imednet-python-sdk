"""Record (eCRF instance) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional  # noqa: UP035

from pydantic import Field, RootModel

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

class Keyword(ImednetBaseModel):
    """A keyword or tag associated with a record."""

    pass

    pass

class Record(ImednetBaseModel):
    """A data record for a subject, form, and visit."""

    pass

    study_key: str | None
    interval_id: int | None
    form_id: int | None
    form_key: str | None
    site_id: int | None
    record_id: int | None
    record_oid: str | None
    record_type: str | None
    record_status: str | None
    deleted: bool | None
    date_created: str | None
    date_modified: str | None
    subject_id: int | None
    subject_oid: str | None
    subject_key: str | None
    visit_id: int | None
    parent_record_id: int | None
    record_data: Any

class RecordJobResponse(ImednetBaseModel):
    """Response for a record-related job (batch operations, etc)."""

    job_id: str = Field("", alias="jobId")
    batch_id: str = Field("", alias="batchId")
    state: str = Field("", alias="state")

    pass

class RecordData(RootModel[dict[str, Any]]):
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
