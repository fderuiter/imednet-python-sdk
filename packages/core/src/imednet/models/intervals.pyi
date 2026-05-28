from datetime import datetime
from typing import Any, Optional, Dict, List
from imednet.models.json_base import JsonModel

class Interval(JsonModel):
    study_key: Optional[str]
    interval_id: Optional[int]
    interval_name: Optional[str]
    interval_description: Optional[str]
    interval_sequence: Optional[int]
    interval_group_id: Optional[int]
    interval_group_name: Optional[str]
    disabled: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]

