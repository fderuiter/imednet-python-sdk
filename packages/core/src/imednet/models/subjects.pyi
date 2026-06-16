from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Subject(JsonModel):
    keywords: Optional[List[SubjectKeyword]]
    study_key: Optional[str]
    subject_id: Optional[int]
    subject_key: Optional[str]
    subject_status: Optional[str]
    site_id: Optional[int]
    site_name: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    subject_oid: Optional[str]
    enrollment_start_date: Optional[str]

class SubjectKeyword(JsonModel):
    keyword_id: Optional[int]
    keyword_key: Optional[str]
    keyword_name: Optional[str]
    date_added: Optional[str]
