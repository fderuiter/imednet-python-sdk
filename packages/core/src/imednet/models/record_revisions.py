"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class RecordRevision(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    record_revision_id: Optional[int] = Field(default=None, alias="recordRevisionId")
    record_id: Optional[int] = Field(default=None, alias="recordId")
    record_revision: Optional[int] = Field(default=None, alias="recordRevision")
    data_revision: Optional[int] = Field(default=None, alias="dataRevision")
    record_status: Optional[str] = Field(default=None, alias="recordStatus")
    subject_id: Optional[int] = Field(default=None, alias="subjectId")
    subject_key: Optional[str] = Field(default=None, alias="subjectKey")
    site_id: Optional[int] = Field(default=None, alias="siteId")
    form_key: Optional[str] = Field(default=None, alias="formKey")
    interval_id: Optional[int] = Field(default=None, alias="intervalId")
    deleted: Optional[bool] = Field(default=None, alias="deleted")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")

    pass
