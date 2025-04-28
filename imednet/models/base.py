"""Base models for the iMedNet SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import (
    parse_datetime,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


class SortField(BaseModel):
    """Sorting information for a field in a paginated response."""

    property: str = Field(..., description="Property to sort by")
    direction: str = Field(..., description="Sort direction (ASC or DESC)")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("property", "direction", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)


class Pagination(BaseModel):
    """Pagination information in an API response."""

    current_page: int = Field(0, alias="currentPage")
    size: int = Field(25, alias="size")
    total_pages: int = Field(0, alias="totalPages")
    total_elements: int = Field(0, alias="totalElements")
    sort: List[SortField] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("current_page", "size", "total_pages", "total_elements", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("sort", mode="before")
    def _fill_list(cls, v):
        return parse_list_or_default(v)


class Error(BaseModel):
    """Error information in an API response."""

    code: str = Field("", description="Error code")
    message: str = Field("", description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("code", "message", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("details", mode="before")
    def _fill_details(cls, v):
        return v if isinstance(v, dict) else {}


class Metadata(BaseModel):
    """Metadata information in an API response."""

    status: str = Field("", description="Response status")
    method: str = Field("", description="HTTP method")
    path: str = Field("", description="Request path")
    timestamp: datetime
    error: Error = Field(default_factory=lambda: Error(code="", message=""))

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("status", "method", "path", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("timestamp", mode="before")
    def _parse_datetime(cls, v):
        return parse_datetime(v)


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response model."""

    metadata: Metadata
    pagination: Optional[Pagination] = None
    data: T

    model_config = ConfigDict(populate_by_name=True)
