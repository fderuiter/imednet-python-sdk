from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class QueryComment(JsonModel):
    user: Optional[str]
    date_created: Optional[str]
    text: Optional[str]
    closed: Optional[bool]
    sequence: Optional[int]

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
    query_comments: List[QueryComment]
