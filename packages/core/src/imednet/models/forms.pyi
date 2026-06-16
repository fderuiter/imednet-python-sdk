from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Form(JsonModel):
    study_key: Optional[str]
    form_id: Optional[int]
    form_key: Optional[str]
    form_name: Optional[str]
    form_type: Optional[str]
    revision: Optional[int]
    date_created: Optional[str]
    date_modified: Optional[str]
    disabled: Optional[bool]
    epro_form: Optional[bool]
    allow_copy: Optional[bool]
    unscheduled_visit: Optional[bool]
