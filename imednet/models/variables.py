import datetime
from dataclasses import dataclass


@dataclass
class Variable:
    study_key: str
    variable_id: int
    variable_type: str
    variable_name: str
    sequence: int
    revision: int
    disabled: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
    form_id: int
    variable_oid: str
    deleted: bool
    form_key: str
    form_name: str
    label: str
    blinded: bool
