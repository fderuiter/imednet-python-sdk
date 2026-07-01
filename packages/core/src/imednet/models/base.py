"""Base models for the iMedNet SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from msgspec import field as Field

from imednet.models.json_base import JsonModel


class ImednetStruct(JsonModel, kw_only=True, omit_defaults=True):
    """Core base model for all iMedNet API responses.

    Design philosophy:
    extra='ignore' silently drops new undocumented fields the API introduces.
    populate_by_name allows models to be instantiated using either pythonic
    snake_case names or original API camelCase names via Field aliases.
    str_strip_whitespace trims leading and trailing whitespace from string values.
    """


class SortField(JsonModel, kw_only=True, omit_defaults=True):
    """Sorting information for a field in a paginated response."""

    property: str 
    direction: str


class Pagination(JsonModel, kw_only=True, omit_defaults=True):
    """Pagination information in an API response."""

    current_page: int = Field(default=0)
    size: int = Field(default=25)
    total_pages: int = Field(default=0)
    total_elements: int = Field(default=0)
    sort: List[SortField] = Field(default_factory=list)


class Error(JsonModel, kw_only=True, omit_defaults=True):
    """Error information in an API response."""

    code: str = Field(default="")
    message: str = Field(default="")
    details: Dict[str, Any] = Field(default_factory=dict)


class Metadata(JsonModel, kw_only=True, omit_defaults=True):
    """Metadata information in an API response."""

    status: str = Field(default="")
    method: str = Field(default="")
    path: str = Field(default="")
    timestamp: datetime
    error: Error = Field(default_factory=lambda: Error(code=""))


T = TypeVar("T")


class ApiResponse(JsonModel, Generic[T], kw_only=True, omit_defaults=True):
    """Generic API response model."""

    metadata: Metadata
    pagination: Optional[Pagination] = None
    data: T
