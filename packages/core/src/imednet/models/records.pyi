from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Record(JsonModel):
    study_key: Optional[str]
    interval_id: Optional[int]
    form_id: Optional[int]
    form_key: Optional[str]
    site_id: Optional[int]
    record_id: Optional[int]
    record_oid: Optional[str]
    record_type: Optional[str]
    record_status: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    subject_id: Optional[int]
    subject_oid: Optional[str]
    subject_key: Optional[str]
    visit_id: Optional[int]
    parent_record_id: Optional[int]
    record_data: Optional[Any]

class Keyword(JsonModel):
    pass

class RecordJobResponse(JsonModel):
    job_id: str
    batch_id: str
    state: str

class RecordData(JsonModel):
    pass

class BaseRecordRequest(JsonModel):
    form_key: str
    data: RecordData

class RegisterSubjectRequest(BaseRecordRequest):
    site_name: str

class UpdateScheduledRecordRequest(BaseRecordRequest):
    subject_key: str
    interval_name: str

class CreateNewRecordRequest(BaseRecordRequest):
    subject_key: str
