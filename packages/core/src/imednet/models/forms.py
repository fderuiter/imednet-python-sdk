"""Form (eCRF) metadata models for iMedNet."""

from __future__ import annotations

from datetime import datetime

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Form(JsonModel, kw_only=True, omit_defaults=True):
    """Configuration and metadata for a CRF (Case Report Form)."""

    subject_record_report: bool | None = Field(default=None)
    unscheduled_visit: bool | None = Field(default=None)
    disabled: bool | None = Field(default=None)


Form = ModelEngine.get_model('Form', Form)
