"""Common data models used across the iMednet API."""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Type variable for generic responses
T = TypeVar("T")


class FieldError(BaseModel):
    """Model for field-specific error details."""

    attribute: str = Field(..., description="The request attribute that caused the error")
    value: str = Field(..., description="The invalid value provided for the problematic attribute")


class ErrorDetail(BaseModel):
    """Model for API error details."""

    code: Optional[str] = Field(None, description="Error code representing the specific error type")
    description: Optional[str] = Field(
        None, description="Description providing details about the error"
    )
    field: Optional[FieldError] = Field(
        None, description="Field-specific error details if applicable"
    )


class SortInfo(BaseModel):
    """Model for sorting parameters."""

    property: str = Field(..., alias="property", description="The field to sort by") # Use alias 'property'
    direction: str = Field(..., description="The sort direction (asc or desc)")


class PaginationInfo(BaseModel):
    """Model for pagination details."""

    currentPage: int = Field(..., alias="currentPage", ge=0, description="Current page number (0-indexed)") # Use alias
    size: int = Field(..., ge=0, description="Number of items per page")
    totalElements: int = Field(..., alias="totalElements", ge=0, description="Total number of elements across all pages") # Use alias
    totalPages: int = Field(..., alias="totalPages", ge=0, description="Total number of pages") # Add totalPages based on mock data
    sort: Optional[List[SortInfo]] = Field(None, description="Sorting information applied")


class Metadata(BaseModel):
    """Model for API response metadata."""

    status: str = Field(..., description="Response status (OK, BAD_REQUEST, etc.)")
    path: Optional[str] = Field(None, description="The API endpoint path")
    timestamp: datetime = Field(..., description="Timestamp of the response")
    error: Optional[ErrorDetail] = Field(None, description="Error details if applicable")


class ApiResponse(BaseModel, Generic[T]):
    """Generic model for API responses."""

    model_config = ConfigDict(
        populate_by_name=True, json_encoders={datetime: lambda dt: dt.isoformat()}
    )

    metadata: Metadata = Field(..., description="Response metadata")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information if applicable") # Add top-level pagination
    data: Optional[T] = Field(None, description="Response data of generic type T")
