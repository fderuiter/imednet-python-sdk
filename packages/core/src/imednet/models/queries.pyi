from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class QueryComment(JsonModel):
    sequence: Optional[int]
    closed: Optional[bool]

class Query(JsonModel):
    study_key: Optional[str]
    subject_id: Optional[int]
    annotation_id: Optional[int]
    description: Optional[str]
    record_id: Optional[int]
    variable: Optional[str]
    subject_key: Optional[str]
    date_created: Optional[str]
    date_modified: Optional[str]
    query_comments: Optional[List[QueryComment]]
