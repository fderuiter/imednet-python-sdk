"""Medical coding models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.base import ImednetBaseModel

class Coding(ImednetBaseModel):
    """Represents a medical coding entry associated with a record."""

    study_key: Optional[str]
    site_name: Optional[str]
    site_id: Optional[int]
    subject_id: Optional[int]
    subject_key: Optional[str]
    form_id: Optional[int]
    form_name: Optional[str]
    form_key: Optional[str]
    record_id: Optional[int]
    variable: Optional[str]
    value: Optional[str]
    coding_id: Optional[str]
    code: Optional[str]
    coded_by: Optional[str]
    dictionary_name: Optional[str]
    dictionary_version: Optional[str]
    date_coded: Optional[str]
    reason: Any
    revision: Any
