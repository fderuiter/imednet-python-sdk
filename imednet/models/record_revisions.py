import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RecordRevision:
    study_key: str
    record_revision_id: int
    record_id: int
    record_oid: str
    record_revision: int
    data_revision: int
    record_status: str
    subject_id: int
    subject_oid: str
    subject_key: str
    site_id: int
    form_key: str
    interval_id: int
    role: str
    user: str
    reason_for_change: str
    deleted: bool
    date_created: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "RecordRevision":
        """
        Create a RecordRevision instance from JSON data.

        Args:
            data: Dictionary containing record revision data from the API

        Returns:
            RecordRevision instance with the data
        """
        # Parse datetime string
        date_created = (
            datetime.datetime.fromisoformat(data.get("dateCreated", "").replace(" ", "T"))
            if data.get("dateCreated")
            else datetime.datetime.now()
        )

        return cls(
            study_key=data.get("studyKey", ""),
            record_revision_id=data.get("recordRevisionId", 0),
            record_id=data.get("recordId", 0),
            record_oid=data.get("recordOid", ""),
            record_revision=data.get("recordRevision", 0),
            data_revision=data.get("dataRevision", 0),
            record_status=data.get("recordStatus", ""),
            subject_id=data.get("subjectId", 0),
            subject_oid=data.get("subjectOid", ""),
            subject_key=data.get("subjectKey", ""),
            site_id=data.get("siteId", 0),
            form_key=data.get("formKey", ""),
            interval_id=data.get("intervalId", 0),
            role=data.get("role", ""),
            user=data.get("user", ""),
            reason_for_change=data.get("reasonForChange", ""),
            deleted=data.get("deleted", False),
            date_created=date_created,
        )
