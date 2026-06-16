from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Form(JsonModel):
    """Configuration and metadata for a CRF (Case Report Form)."""
    
    unscheduled_visit: Optional[bool] = Field(None, alias="unscheduledVisit")
    subject_record_report: Optional[bool] = Field(None, alias="subjectRecordReport")

Form = ModelEngine.get_model('Form', Form)
