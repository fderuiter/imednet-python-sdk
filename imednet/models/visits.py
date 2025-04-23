import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional


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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Visit":
        """
        Create a Visit instance from JSON data.

        Args:
            data: Dictionary containing visit data from the API

        Returns:
            Visit instance with the data
        """
        # Parse date strings
        start_date = None
        if data.get("startDate"):
            start_date = datetime.date.fromisoformat(data["startDate"])

        end_date = None
        if data.get("endDate"):
            end_date = datetime.date.fromisoformat(data["endDate"])

        due_date = None
        if data.get("dueDate"):
            due_date = datetime.date.fromisoformat(data["dueDate"])

        visit_date = None
        if data.get("visitDate"):
            visit_date = datetime.date.fromisoformat(data["visitDate"])

        # Parse datetime strings
        date_created = (
            datetime.datetime.fromisoformat(data.get("dateCreated", "").replace(" ", "T"))
            if data.get("dateCreated")
            else datetime.datetime.now()
        )

        date_modified = (
            datetime.datetime.fromisoformat(data.get("dateModified", "").replace(" ", "T"))
            if data.get("dateModified")
            else datetime.datetime.now()
        )

        return cls(
            visit_id=data.get("visitId", 0),
            study_key=data.get("studyKey", ""),
            interval_id=data.get("intervalId", 0),
            interval_name=data.get("intervalName", ""),
            subject_id=data.get("subjectId", 0),
            subject_key=data.get("subjectKey", ""),
            start_date=start_date,
            end_date=end_date,
            due_date=due_date,
            visit_date=visit_date,
            visit_date_form=data.get("visitDateForm", ""),
            visit_date_question=data.get("visitDateQuestion", ""),
            deleted=data.get("deleted", False),
            date_created=date_created,
            date_modified=date_modified,
        )
