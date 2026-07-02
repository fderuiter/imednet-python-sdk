"""Query and annotation models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.base import ImednetBaseModel


class QueryComment(ImednetBaseModel):
    """A comment or response within a data query thread."""

    closed: bool | None = Field(default=None, alias="closed")
    sequence: int | None = Field(default=None, alias="sequence")
    annotation_status: str | None = Field(default=None, alias="annotationStatus")
    user: str | None = Field(default=None, alias="user")
    comment: str | None = Field(default=None, alias="comment")
    date: str | None = Field(default=None, alias="date")


QueryComment = ModelEngine.get_model('QueryComment', QueryComment)


class Query(ImednetBaseModel):
    """Represents a data query (discrepancy) raised on a record."""

    query_comments: List[QueryComment] = Field(default_factory=list, alias="queryComments")


Query = ModelEngine.get_model('Query', Query)
