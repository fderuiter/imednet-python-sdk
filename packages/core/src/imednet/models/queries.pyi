"""Query and annotation models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional  # noqa: UP035

from pydantic import Field

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

class QueryComment(ImednetBaseModel):
    """A comment or response within a data query thread."""

    closed: bool | None = Field(default=None, alias="closed")
    sequence: int | None = Field(default=None, alias="sequence")
    annotation_status: str | None = Field(default=None, alias="annotationStatus")
    user: str | None = Field(default=None, alias="user")
    comment: str | None = Field(default=None, alias="comment")
    date: str | None = Field(default=None, alias="date")

class Query(ImednetBaseModel):
    """Represents a data query (discrepancy) raised on a record."""

    query_comments: list[QueryComment] = Field(default_factory=list, alias="queryComments")

    study_key: str | None
    subject_id: int | None
    annotation_id: int | None
    description: str | None
    record_id: int | None
    variable: str | None
    subject_key: str | None
    date_created: str | None
    date_modified: str | None
    annotation_type: Any
    subject_oid: Any
    type: Any
