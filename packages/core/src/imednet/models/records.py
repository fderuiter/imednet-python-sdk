"""Record (eCRF instance) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Keyword(JsonModel, kw_only=True, omit_defaults=True):
    """A keyword or tag associated with a record."""

    pass


Keyword = ModelEngine.get_model('Keyword', Keyword)


class Record(JsonModel, kw_only=True, omit_defaults=True):
    """A data record for a subject, form, and visit."""

    pass


Record = ModelEngine.get_model('Record', Record)


class RecordJobResponse(JsonModel, kw_only=True, omit_defaults=True):
    """Response for a record-related job (batch operations, etc)."""

    job_id: str = Field(default="")
    batch_id: str = Field(default="")
    state: str = Field(default="")

    pass


RecordData = Dict[str, Any]
class _Dummy:
    """Arbitrary record data as a dictionary."""

    pass


class BaseRecordRequest(JsonModel, kw_only=True, omit_defaults=True):
    """Base class for record creation/update requests."""

    form_key: str = Field(default="")
    data: RecordData = Field(default_factory=lambda: RecordData({}), name="data")

    pass


class RegisterSubjectRequest(BaseRecordRequest):
    """Payload for registering (enrolling) a new subject.

    Per the API documentation, registering a subject only requires ``formKey``
    and ``siteName``.  The system assigns the subject identifier upon creation.
    Do **not** include a ``subjectKey`` here — doing so causes the server to
    treat the request as an update and reject it when the key is unknown.
    """

    site_name: str = Field(default="", name="siteName")

    pass


class UpdateScheduledRecordRequest(BaseRecordRequest):
    """Payload for updating an existing scheduled record."""

    subject_key: str = Field(default="")
    interval_name: str = Field(default="")

    pass


class CreateNewRecordRequest(BaseRecordRequest):
    """Payload for creating a new unscheduled record."""

    subject_key: str = Field(default="")

    pass
