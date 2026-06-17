from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class QueryComment(JsonModel):
    """A comment or response within a data query thread."""

    annotation_status: Optional[str] = Field(None, alias="annotationStatus")
    comment: Optional[str] = Field(None)
    date: Optional[str] = Field(None)
    user: Optional[str] = Field(None)

    sequence: int = Field(default=0)
    closed: bool = Field(default=False)


QueryComment = ModelEngine.get_model('QueryComment', QueryComment)


class Query(JsonModel):
    """Represents a data query (discrepancy) raised on a record."""

    query_comments: List[QueryComment] = Field(default_factory=list, alias="queryComments")


Query = ModelEngine.get_model('Query', Query)
