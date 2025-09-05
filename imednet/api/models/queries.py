from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .json_base import JsonModel


class QueryComment(JsonModel):
    """Represents a single comment on a query."""

    sequence: int = Field(0, alias="sequence", description="The sequence number of the comment.")
    annotation_status: str = Field(
        "", alias="annotationStatus", description="The status of the annotation."
    )
    user: str = Field("", alias="user", description="The user who made the comment.")
    comment: str = Field("", alias="comment", description="The text of the comment.")
    closed: bool = Field(
        False,
        alias="closed",
        description="Indicates if the query was closed by this comment.",
    )
    date: datetime = Field(
        default_factory=datetime.now,
        alias="date",
        description="The date the comment was made.",
    )


class Query(JsonModel):
    """Represents a data query in the system."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    subject_id: int = Field(0, alias="subjectId", description="The ID of the subject.")
    subject_oid: str = Field("", alias="subjectOid", description="The OID of the subject.")
    annotation_type: str = Field(
        "", alias="annotationType", description="The type of the annotation."
    )
    annotation_id: int = Field(0, alias="annotationId", description="The ID of the annotation.")
    type: Optional[str] = Field(None, alias="type", description="The type of the query.")
    description: str = Field("", alias="description", description="The description of the query.")
    record_id: int = Field(0, alias="recordId", description="The ID of the record.")
    variable: str = Field(
        "", alias="variable", description="The variable the query is associated with."
    )
    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the query was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the query was last modified.",
    )
    query_comments: List[QueryComment] = Field(
        default_factory=list, alias="queryComments", description="A list of comments on the query."
    )
