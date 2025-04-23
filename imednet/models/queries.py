import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class QueryComment:
    sequence: int
    annotation_status: str
    user: str
    comment: str
    closed: bool
    date: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "QueryComment":
        """
        Create a QueryComment instance from JSON data.

        Args:
            data: Dictionary containing query comment data from the API

        Returns:
            QueryComment instance with the data
        """
        # Parse datetime string
        date = (
            datetime.datetime.fromisoformat(data.get("date", "").replace(" ", "T"))
            if data.get("date")
            else datetime.datetime.now()
        )

        return cls(
            sequence=data.get("sequence", 0),
            annotation_status=data.get("annotationStatus", ""),
            user=data.get("user", ""),
            comment=data.get("comment", ""),
            closed=data.get("closed", False),
            date=date,
        )


@dataclass
class Query:
    study_key: str
    subject_id: int
    subject_oid: str
    annotation_type: str
    annotation_id: int
    type: Optional[str]
    description: str
    record_id: int
    variable: str
    subject_key: str
    date_created: datetime.datetime
    date_modified: datetime.datetime
    query_comments: List[QueryComment]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Query":
        """
        Create a Query instance from JSON data.

        Args:
            data: Dictionary containing query data from the API

        Returns:
            Query instance with the data
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

        # Handle nested query comments
        query_comments = []
        comments_data = data.get("queryComments", [])
        for comment_data in comments_data:
            query_comments.append(QueryComment.from_json(comment_data))

        return cls(
            study_key=data.get("studyKey", ""),
            subject_id=data.get("subjectId", 0),
            subject_oid=data.get("subjectOid", ""),
            annotation_type=data.get("annotationType", ""),
            annotation_id=data.get("annotationId", 0),
            type=data.get("type"),
            description=data.get("description", ""),
            record_id=data.get("recordId", 0),
            variable=data.get("variable", ""),
            subject_key=data.get("subjectKey", ""),
            date_created=date_created,
            date_modified=date_modified,
            query_comments=query_comments,
        )
