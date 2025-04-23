import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Job:
    job_id: str
    batch_id: str
    state: str
    date_created: datetime.datetime
    date_started: datetime.datetime
    date_finished: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Job":
        """
        Create a Job instance from JSON data.

        Args:
            data: Dictionary containing job data from the API

        Returns:
            Job instance with the data
        """
        # Parse datetime strings
        date_created = _parse_datetime(data.get("dateCreated"))
        date_started = _parse_datetime(data.get("dateStarted"))
        date_finished = _parse_datetime(data.get("dateFinished"))

        return cls(
            job_id=data.get("jobId", ""),
            batch_id=data.get("batchId", ""),
            state=data.get("state", ""),
            date_created=date_created,
            date_started=date_started,
            date_finished=date_finished,
        )


def _parse_datetime(date_str: Optional[str]) -> datetime.datetime:
    """
    Helper function to parse datetime strings from the API.

    Args:
        date_str: ISO format date string or None

    Returns:
        Parsed datetime object or current time if None
    """
    if not date_str:
        return datetime.datetime.now()

    return datetime.datetime.fromisoformat(date_str.replace(" ", "T"))
