import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class QueryComment:
    sequence: int
    annotation_status: str
    user: str
    comment: str
    closed: bool
    date: datetime.datetime


@dataclass
class Query:
    study_key: str
    subject_id: int
    subject_oid: str
    annotation_type: str
    annotation_id: int
    type: Optional[str]
    description: str
    record_id: int
    variable: str
    subject_key: str
    date_created: datetime.datetime
    date_modified: datetime.datetime
    query_comments: List[QueryComment]
