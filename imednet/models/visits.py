import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Visit:
    visit_id: int
    study_key: str
    interval_id: int
    interval_name: str
    subject_id: int
    subject_key: str
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]
    due_date: Optional[datetime.date]
    visit_date: Optional[datetime.date]
    visit_date_form: str
    visit_date_question: str
    deleted: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
