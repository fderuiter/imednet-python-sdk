from datetime import datetime
from typing import Any, Optional, Dict, List
from imednet.models.json_base import JsonModel

class Visit(JsonModel):
    visit_id: Optional[int]
    study_key: Optional[str]
    interval_id: Optional[int]
    interval_name: Optional[str]
    subject_id: Optional[int]
    subject_key: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    due_date: Optional[str]
    visit_date: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]

