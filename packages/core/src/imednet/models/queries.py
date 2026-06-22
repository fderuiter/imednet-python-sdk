"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class QueryComment(JsonModel):
    """TODO: Add docstring."""

    user: Optional[str] = Field(default=None, alias="user")
    date: Optional[str] = Field(default=None, alias="date")
    comment: Optional[str] = Field(default=None, alias="comment")
    annotation_status: Optional[str] = Field(default=None, alias="annotationStatus")
    closed: Optional[bool] = Field(default=None, alias="closed")
    sequence: Optional[int] = Field(default=None, alias="sequence")



class Query(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    subject_id: Optional[int] = Field(default=None, alias="subjectId")
    annotation_id: Optional[int] = Field(default=None, alias="annotationId")
    description: Optional[str] = Field(default=None, alias="description")
    record_id: Optional[int] = Field(default=None, alias="recordId")
    variable: Optional[str] = Field(default=None, alias="variable")
    subject_key: Optional[str] = Field(default=None, alias="subjectKey")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")
    query_comments: List[QueryComment] = Field(default_factory=list, alias="queryComments")

