import datetime
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SubjectKeyword:
    keyword_name: str
    keyword_key: str
    keyword_id: int
    date_added: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "SubjectKeyword":
        """
        Create a SubjectKeyword instance from JSON data.

        Args:
            data: Dictionary containing keyword data from the API

        Returns:
            SubjectKeyword instance with the data
        """
        # Parse datetime string
        date_added = (
            datetime.datetime.fromisoformat(data.get("dateAdded", "").replace(" ", "T"))
            if data.get("dateAdded")
            else datetime.datetime.now()
        )

        return cls(
            keyword_name=data.get("keywordName", ""),
            keyword_key=data.get("keywordKey", ""),
            keyword_id=data.get("keywordId", 0),
            date_added=date_added,
        )


@dataclass
class Subject:
    study_key: str
    subject_id: int
    subject_oid: str
    subject_key: str
    subject_status: str
    site_id: int
    site_name: str
    deleted: bool
    enrollment_start_date: datetime.datetime
    date_created: datetime.datetime
    date_modified: datetime.datetime
    keywords: List[SubjectKeyword]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Subject":
        """
        Create a Subject instance from JSON data.

        Args:
            data: Dictionary containing subject data from the API

        Returns:
            Subject instance with the data
        """
        # Parse datetime strings
        enrollment_start_date = (
            datetime.datetime.fromisoformat(data.get("enrollmentStartDate", "").replace(" ", "T"))
            if data.get("enrollmentStartDate")
            else datetime.datetime.now()
        )

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

        # Handle nested keywords
        keywords = []
        keywords_data = data.get("keywords", [])
        for keyword_data in keywords_data:
            keywords.append(SubjectKeyword.from_json(keyword_data))

        return cls(
            study_key=data.get("studyKey", ""),
            subject_id=data.get("subjectId", 0),
            subject_oid=data.get("subjectOid", ""),
            subject_key=data.get("subjectKey", ""),
            subject_status=data.get("subjectStatus", ""),
            site_id=data.get("siteId", 0),
            site_name=data.get("siteName", ""),
            deleted=data.get("deleted", False),
            enrollment_start_date=enrollment_start_date,
            date_created=date_created,
            date_modified=date_modified,
            keywords=keywords,
        )
