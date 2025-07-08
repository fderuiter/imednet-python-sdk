from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class QueryComment(JsonModel):
    sequence: int = Field(0, alias="sequence")
    annotation_status: str = Field("", alias="annotationStatus")
    user: str = Field("", alias="user")
    comment: str = Field("", alias="comment")
    closed: bool = Field(False, alias="closed")
    date: datetime = Field(default_factory=datetime.now, alias="date")

    pass


class Query(JsonModel):
    study_key: str = Field("", alias="studyKey")
    subject_id: int = Field(0, alias="subjectId")
    subject_oid: str = Field("", alias="subjectOid")
    annotation_type: str = Field("", alias="annotationType")
    annotation_id: int = Field(0, alias="annotationId")
    type: Optional[str] = Field(None, alias="type")
    description: str = Field("", alias="description")
    record_id: int = Field(0, alias="recordId")
    variable: str = Field("", alias="variable")
    subject_key: str = Field("", alias="subjectKey")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    query_comments: List[QueryComment] = Field(default_factory=list, alias="queryComments")

    pass
