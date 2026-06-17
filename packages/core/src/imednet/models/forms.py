from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Form(JsonModel):
    """Configuration and metadata for a CRF (Case Report Form)."""

    form_id: Optional[int] = Field(None, alias="formId")
    unscheduled_visit: Optional[bool] = Field(None, alias="unscheduledVisit")
    subject_record_report: Optional[bool] = Field(None, alias="subjectRecordReport")
    disabled: Optional[bool] = Field(None, alias="disabled")
    form_key: Optional[str] = Field(None, alias="formKey")
    embedded_log: Optional[bool] = Field(None, alias="embeddedLog")
    enforce_ownership: Optional[bool] = Field(None, alias="enforceOwnership")
    user_agreement: Optional[bool] = Field(None, alias="userAgreement")
    other_forms: Optional[bool] = Field(None, alias="otherForms")


Form = ModelEngine.get_model('Form', Form)
