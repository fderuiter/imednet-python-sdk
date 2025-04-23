import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Site:
    study_key: str
    site_id: int
    site_name: str
    site_enrollment_status: str
    date_created: datetime.datetime
    date_modified: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Site":
        """
        Create a Site instance from JSON data.

        Args:
            data: Dictionary containing site data from the API

        Returns:
            Site instance with the data
        """
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
            study_key=data.get("studyKey", ""),
            site_id=data.get("siteId", 0),
            site_name=data.get("siteName", ""),
            site_enrollment_status=data.get("siteEnrollmentStatus", ""),
            date_created=date_created,
            date_modified=date_modified,
        )
