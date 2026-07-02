"""Form (eCRF) metadata models for iMedNet."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel



class Form(JsonModel):
    study_key: Optional[str]
    form_id: Optional[int]
    form_key: Optional[str]
    form_name: Optional[str]
    form_type: Optional[str]
    revision: Optional[int]
    date_created: Optional[str]
    date_modified: Optional[str]
    disabled: Optional[bool]
    epro_form: Optional[bool]
    allow_copy: Optional[bool]
    embedded_log: Any
    enforce_ownership: Any
    other_forms: Any
    user_agreement: Any

