"""Models for subjects and participant keywords."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel



class SubjectKeyword(JsonModel):
    pass


class Subject(JsonModel):
    study_key: Optional[str]
    subject_id: Optional[int]
    subject_key: Optional[str]
    subject_status: Optional[str]
    site_id: Optional[int]
    site_name: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    enrollment_start_date: Any
    subject_oid: Any

