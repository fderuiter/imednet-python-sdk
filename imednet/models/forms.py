import datetime
from dataclasses import dataclass


@dataclass
class Form:
    study_key: str
    form_id: int
    form_key: str
    form_name: str
    form_type: str
    revision: int
    embedded_log: bool
    enforce_ownership: bool
    user_agreement: bool
    subject_record_report: bool
    unscheduled_visit: bool
    other_forms: bool
    epro_form: bool
    allow_copy: bool
    disabled: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
