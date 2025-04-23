import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class SubjectKeyword:
    keyword_name: str
    keyword_key: str
    keyword_id: int
    date_added: datetime.datetime


@dataclass
class Subject:
    study_key: str
    subject_id: int
    subject_oid: str
    subject_key: str
    subject_status: str
    site_id: int
    site_name: str
    deleted: bool
    enrollment_start_date: datetime.datetime
    date_created: datetime.datetime
    date_modified: datetime.datetime
    keywords: List[SubjectKeyword]
