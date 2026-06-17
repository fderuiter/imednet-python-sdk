from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Interval(JsonModel):
    study_key: Optional[str]
    interval_id: Optional[int]
    interval_name: Optional[str]
    interval_description: Optional[str]
    interval_sequence: Optional[int]
    interval_group_id: Optional[int]
    interval_group_name: Optional[str]
    disabled: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    actual_date: Optional[str]
    actual_date_form: Optional[str]
    defined_using_interval: Optional[str]
    due_date_will_be_in: Optional[str]
    epro_grace_period: Optional[int]
    negative_slack: Optional[int]
    positive_slack: Optional[int]
    timeline: Optional[str]
    window_calculation_date: Optional[str]
    window_calculation_form: Optional[str]


class FormSummary(JsonModel): ...
