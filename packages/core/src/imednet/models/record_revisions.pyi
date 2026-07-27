"""Record revision history models for iMedNet."""

from __future__ import annotations

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

from typing import Any, Optional


class RecordRevision(ImednetBaseModel):
    """Historical version of a record including change reason and user."""

    study_key: Optional[str]
    record_revision_id: Optional[int]
    record_id: Optional[int]
    record_revision: Optional[int]
    data_revision: Optional[int]
    record_status: Optional[str]
    subject_id: Optional[int]
    subject_key: Optional[str]
    site_id: Optional[int]
    form_key: Optional[str]
    interval_id: Optional[int]
    deleted: Optional[bool]
    date_created: Optional[str]
    reason_for_change: Any
    record_oid: Any
    role: Any
    subject_oid: Any
    user: Any
    last_updated: Optional[str]
