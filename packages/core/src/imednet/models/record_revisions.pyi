"""Record revision history models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

class RecordRevision(ImednetBaseModel):
    """Historical version of a record including change reason and user."""

    pass

    study_key: str | None
    record_revision_id: int | None
    record_id: int | None
    record_revision: int | None
    data_revision: int | None
    record_status: str | None
    subject_id: int | None
    subject_key: str | None
    site_id: int | None
    form_key: str | None
    interval_id: int | None
    deleted: bool | None
    date_created: str | None
    reason_for_change: Any
    record_oid: Any
    role: Any
    subject_oid: Any
    user: Any
