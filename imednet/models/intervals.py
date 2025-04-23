import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class FormSummary:
    form_id: int
    form_key: str
    form_name: str


@dataclass
class Interval:
    study_key: str
    interval_id: int
    interval_name: str
    interval_description: str
    interval_sequence: int
    interval_group_id: int
    interval_group_name: str
    disabled: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
    timeline: str
    defined_using_interval: str
    window_calculation_form: str
    window_calculation_date: str
    actual_date_form: str
    actual_date: str
    due_date_will_be_in: int
    negative_slack: int
    positive_slack: int
    epro_grace_period: int
    forms: List[FormSummary]
