from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Form(JsonModel):
    """Configuration and metadata for a CRF (Case Report Form)."""

    embedded_log: bool | None = Field(default=None, alias="embeddedLog")
    enforce_ownership: bool | None = Field(default=None, alias="enforceOwnership")
    user_agreement: bool | None = Field(default=None, alias="userAgreement")
    subject_record_report: bool | None = Field(default=None, alias="subjectRecordReport")
    unscheduled_visit: bool | None = Field(default=None, alias="unscheduledVisit")
    other_forms: bool | None = Field(default=None, alias="otherForms")


Form = ModelEngine.get_model('Form', Form)
