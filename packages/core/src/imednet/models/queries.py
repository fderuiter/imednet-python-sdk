"""Query and annotation models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class QueryComment(JsonModel, kw_only=True, omit_defaults=True):
    """A comment or response within a data query thread."""

    closed: bool | None = Field(default=None)
    sequence: int | None = Field(default=None)
    annotation_status: str | None = Field(default=None)
    user: str | None = Field(default=None)
    comment: str | None = Field(default=None)
    date: str | None = Field(default=None)


QueryComment = ModelEngine.get_model('QueryComment', QueryComment)


class Query(JsonModel, kw_only=True, omit_defaults=True):
    """Represents a data query (discrepancy) raised on a record."""

    query_comments: List[QueryComment] = Field(default_factory=list)


Query = ModelEngine.get_model('Query', Query)
