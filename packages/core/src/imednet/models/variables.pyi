from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Variable(JsonModel):
    study_key: Optional[str]
    variable_id: Optional[int]
    variable_type: Optional[str]
    variable_name: Optional[str]
    sequence: Optional[int]
    revision: Optional[int]
    date_created: Optional[str]
    date_modified: Optional[str]
    form_id: Optional[int]
    form_key: Optional[str]
    form_name: Optional[str]
    label: Optional[str]
    variable_oid: Optional[str]
