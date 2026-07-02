"""Record (eCRF instance) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import Field, RootModel

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel



class Keyword(JsonModel):
    pass


class Record(JsonModel):
    study_key: Optional[str]
    interval_id: Optional[int]
    form_id: Optional[int]
    form_key: Optional[str]
    site_id: Optional[int]
    record_id: Optional[int]
    record_oid: Optional[str]
    record_type: Optional[str]
    record_status: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    subject_id: Optional[int]
    subject_oid: Optional[str]
    subject_key: Optional[str]
    visit_id: Optional[int]
    parent_record_id: Optional[int]
    record_data: Any

