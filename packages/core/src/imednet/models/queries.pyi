"""Query and annotation models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel

class QueryComment(JsonModel):
    """A comment or response within a data query thread."""

    closed: bool | None = Field(default=None, alias="closed")
    sequence: int | None = Field(default=None, alias="sequence")
    annotation_status: str | None = Field(default=None, alias="annotationStatus")
    user: str | None = Field(default=None, alias="user")
    comment: str | None = Field(default=None, alias="comment")
    date: str | None = Field(default=None, alias="date")

class Query(JsonModel):
    """Represents a data query (discrepancy) raised on a record."""

    query_comments: List[QueryComment] = Field(default_factory=list, alias="queryComments")

    study_key: Optional[str]
    subject_id: Optional[int]
    annotation_id: Optional[int]
    description: Optional[str]
    record_id: Optional[int]
    variable: Optional[str]
    subject_key: Optional[str]
    date_created: Optional[str]
    date_modified: Optional[str]
    annotation_type: Any
    subject_oid: Any
    type: Any
