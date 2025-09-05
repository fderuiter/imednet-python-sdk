"""Base models for the iMedNet SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import Field

from .json_base import JsonModel


class SortField(JsonModel):
    """Defines the sorting criteria for a field in a paginated API response."""

    property: str = Field(
        ...,
        description="The name of the property to sort by.",
    )
    direction: str = Field(
        ...,
        description="The sort direction, either 'ASC' for ascending or 'DESC' for descending.",
    )


class Pagination(JsonModel):
    """Contains pagination details from a paginated API response."""

    current_page: int = Field(0, alias="currentPage", description="The current page number.")
    size: int = Field(25, alias="size", description="The number of items per page.")
    total_pages: int = Field(0, alias="totalPages", description="The total number of pages.")
    total_elements: int = Field(
        0,
        alias="totalElements",
        description="The total number of items across all pages.",
    )
    sort: List[SortField] = Field(
        default_factory=list,
        description="A list of sorting criteria applied to the response.",
    )


class Error(JsonModel):
    """Represents an error object in an API response."""

    code: str = Field("", description="A machine-readable error code.")
    message: str = Field("", description="A human-readable error message.")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="A dictionary of additional error details."
    )


class Metadata(JsonModel):
    """Contains metadata about an API response."""

    status: str = Field("", description="The status of the response (e.g., 'OK', 'ERROR').")
    method: str = Field("", description="The HTTP method of the request (e.g., 'GET', 'POST').")
    path: str = Field("", description="The path of the API request.")
    timestamp: datetime = Field(
        ..., description="The timestamp of when the response was generated."
    )
    error: Error = Field(
        default_factory=lambda: Error(code="", message=""),
        description="Details of the error, if one occurred.",
    )


T = TypeVar("T")


class ApiResponse(JsonModel, Generic[T]):
    """A generic container for all API responses."""

    metadata: Metadata = Field(..., description="Metadata about the API response.")
    pagination: Optional[Pagination] = Field(
        None, description="Pagination information, if the response is paginated."
    )
    data: T = Field(..., description="The main data payload of the response.")
