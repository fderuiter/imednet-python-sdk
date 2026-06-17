from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class RecordRevision(JsonModel):
    study_key: Optional[str]
    record_revision_id: Optional[int]
    record_id: Optional[int]
    record_revision: Optional[int]
    data_revision: Optional[int]
    record_status: Optional[str]
    subject_id: Optional[int]
    subject_key: Optional[str]
    site_id: Optional[int]
    form_key: Optional[str]
    interval_id: Optional[int]
    deleted: Optional[bool]
    date_created: Optional[str]
    reason_for_change: Optional[str]
    record_oid: Optional[str]
    role: Optional[str]
    subject_oid: Optional[str]
    user: Optional[str]
