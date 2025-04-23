import datetime
from dataclasses import dataclass


@dataclass
class RecordRevision:
    study_key: str
    record_revision_id: int
    record_id: int
    record_oid: str
    record_revision: int
    data_revision: int
    record_status: str
    subject_id: int
    subject_oid: str
    subject_key: str
    site_id: int
    form_key: str
    interval_id: int
    role: str
    user: str
    reason_for_change: str
    deleted: bool
    date_created: datetime.datetime
