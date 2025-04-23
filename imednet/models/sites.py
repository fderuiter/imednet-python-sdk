import datetime
from dataclasses import dataclass


@dataclass
class Site:
    study_key: str
    site_id: int
    site_name: str
    site_enrollment_status: str
    date_created: datetime.datetime
    date_modified: datetime.datetime
