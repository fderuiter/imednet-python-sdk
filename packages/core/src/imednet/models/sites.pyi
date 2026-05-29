from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Site(JsonModel):
    study_key: Optional[str]
    site_id: Optional[int]
    site_name: Optional[str]
    site_enrollment_status: Optional[str]
    date_created: Optional[str]
    date_modified: Optional[str]
