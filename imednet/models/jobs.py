import datetime
from dataclasses import dataclass


@dataclass
class Job:
    job_id: str
    batch_id: str
    state: str
    date_created: datetime.datetime
    date_started: datetime.datetime
    date_finished: datetime.datetime
