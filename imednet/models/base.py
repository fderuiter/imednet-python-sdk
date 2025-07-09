"""Base models for the iMedNet SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import Field

from imednet.models.json_base import JsonModel


class SortField(JsonModel):
    """Sorting information for a field in a paginated response."""

    property: str = Field(..., description="Property to sort by")
    direction: str = Field(..., description="Sort direction (ASC or DESC)")

    pass


class Pagination(JsonModel):
    """Pagination information in an API response."""

    current_page: int = Field(0, alias="currentPage")
    size: int = Field(25, alias="size")
    total_pages: int = Field(0, alias="totalPages")
    total_elements: int = Field(0, alias="totalElements")
    sort: List[SortField] = Field(default_factory=list)

    pass


class Error(JsonModel):
    """Error information in an API response."""

    code: str = Field("", description="Error code")
    message: str = Field("", description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict)

    pass


class Metadata(JsonModel):
    """Metadata information in an API response."""

    status: str = Field("", description="Response status")
    method: str = Field("", description="HTTP method")
    path: str = Field("", description="Request path")
    timestamp: datetime
    error: Error = Field(default_factory=lambda: Error(code="", message=""))

    pass


T = TypeVar("T")


class ApiResponse(JsonModel, Generic[T]):
    """Generic API response model."""

    metadata: Metadata
    pagination: Optional[Pagination] = None
    data: T

    pass
