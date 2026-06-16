from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Keyword(JsonModel):
    keyword_id: Optional[int]
    keyword_key: Optional[str]
    keyword_name: Optional[str]
    date_added: Optional[str]

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
    record_data: Optional[Any]
    keywords: Optional[List[Keyword]]
    embedded_log: Optional[Any]
