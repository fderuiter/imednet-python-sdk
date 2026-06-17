from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

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
    keywords: List[SubjectKeyword]
    enrollment_start_date: Optional[str]

class SubjectKeyword(JsonModel):
    keyword_name: str
