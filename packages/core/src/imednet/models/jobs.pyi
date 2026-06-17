from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class Job(JsonModel):
    job_id: Optional[str]
    batch_id: Optional[str]
    state: Optional[str]
    date_created: Optional[str]
    date_finished: Optional[str]
    date_started: Optional[str]


class JobStatus(JsonModel):
    job_id: Optional[str]
    batch_id: Optional[str]
    state: Optional[str]
    date_created: Optional[str]
    date_started: Optional[str]
    date_finished: Optional[str]
    progress: Optional[int]
    result_url: Optional[str]
