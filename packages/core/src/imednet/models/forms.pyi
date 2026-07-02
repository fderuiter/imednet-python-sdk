"""Form (eCRF) metadata models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel

class Form(JsonModel):
    """Configuration and metadata for a CRF (Case Report Form)."""

    study_key: Optional[str]
    form_id: Optional[int]
    form_key: Optional[str]
    form_name: Optional[str]
    form_type: Optional[str]
    revision: Optional[int]
    date_created: Optional[str]
    date_modified: Optional[str]
    epro_form: Optional[bool]
    allow_copy: Optional[bool]
    embedded_log: Any
    enforce_ownership: Any
    other_forms: Any
    user_agreement: Any

    subject_record_report: bool | None = Field(default=None, alias="subjectRecordReport")
    unscheduled_visit: bool | None = Field(default=None, alias="unscheduledVisit")
    disabled: bool | None = Field(default=None, alias="disabled")
