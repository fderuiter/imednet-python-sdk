import datetime
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Keyword:
    keyword_name: str
    keyword_key: str
    keyword_id: int
    date_added: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Keyword":
        """
        Create a Keyword instance from JSON data.

        Args:
            data: Dictionary containing keyword data from the API

        Returns:
            Keyword instance with the data
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
class Record:
    study_key: str
    interval_id: int
    form_id: int
    form_key: str
    site_id: int
    record_id: int
    record_oid: str
    record_type: str
    record_status: str
    deleted: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
    subject_id: int
    subject_oid: str
    subject_key: str
    visit_id: int
    parent_record_id: int
    keywords: List[Keyword]
    record_data: Dict[str, Any]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Record":
        """
        Create a Record instance from JSON data.

        Args:
            data: Dictionary containing record data from the API

        Returns:
            Record instance with the data
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

        # Handle nested keywords
        keywords = []
        keywords_data = data.get("keywords", [])
        for keyword_data in keywords_data:
            keywords.append(Keyword.from_json(keyword_data))

        return cls(
            study_key=data.get("studyKey", ""),
            interval_id=data.get("intervalId", 0),
            form_id=data.get("formId", 0),
            form_key=data.get("formKey", ""),
            site_id=data.get("siteId", 0),
            record_id=data.get("recordId", 0),
            record_oid=data.get("recordOid", ""),
            record_type=data.get("recordType", ""),
            record_status=data.get("recordStatus", ""),
            deleted=data.get("deleted", False),
            date_created=date_created,
            date_modified=date_modified,
            subject_id=data.get("subjectId", 0),
            subject_oid=data.get("subjectOid", ""),
            subject_key=data.get("subjectKey", ""),
            visit_id=data.get("visitId", 0),
            parent_record_id=data.get("parentRecordId", 0),
            keywords=keywords,
            record_data=data.get("recordData", {}),
        )
