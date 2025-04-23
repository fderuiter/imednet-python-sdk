import datetime
from dataclasses import dataclass


@dataclass
class Coding:
    study_key: str
    site_name: str
    site_id: int
    subject_id: int
    subject_key: str
    form_id: int
    form_name: str
    form_key: str
    revision: int
    record_id: int
    variable: str
    value: str
    coding_id: int
    code: str
    coded_by: str
    reason: str
    dictionary_name: str
    dictionary_version: str
    date_coded: datetime.datetime
