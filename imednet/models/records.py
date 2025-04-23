import datetime
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Keyword:
    keyword_name: str
    keyword_key: str
    keyword_id: int
    date_added: datetime.datetime


@dataclass
class Record:
    study_key: str
    interval_id: int
    form_id: int
    form_key: str
    site_id: int
    record_id: int
    record_oid: str
    record_type: str
    record_status: str
    deleted: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
    subject_id: int
    subject_oid: str
    subject_key: str
    visit_id: int
    parent_record_id: int
    keywords: List[Keyword]
    record_data: Dict[str, Any]
