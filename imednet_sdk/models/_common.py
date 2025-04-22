"""Common Pydantic models used across the iMednet SDK.

This module defines base Pydantic models shared by various API responses
and requests, such as error details, pagination information, and the
generic `ApiResponse` wrapper.
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Type variable for generic responses
T = TypeVar("T")


class FieldError(BaseModel):
    """Represents details about an error related to a specific request field.

    Used within `ErrorDetail` when an API error pertains to a particular
    input attribute and its value.

    Attributes:
        attribute: The name of the request attribute that caused the error.
        value: The invalid value provided for the problematic attribute.
    """

    attribute: str = Field(..., description="The request attribute that caused the error")
    value: str = Field(..., description="The invalid value provided for the problematic attribute")


class ErrorDetail(BaseModel):
    """Represents the structure of error information returned by the iMednet API.

    Included in the `metadata` of an `ApiResponse` when an error occurs.

    Attributes:
        code: An optional error code string representing the specific error type
              (e.g., "1000" for validation errors).
        description: An optional human-readable description providing details
                     about the error.
        field: Optional `FieldError` details if the error is specific to a
               request field.
    """

    code: Optional[str] = Field(None, description="Error code representing the specific error type")
    description: Optional[str] = Field(
        None, description="Description providing details about the error"
    )
    field: Optional[FieldError] = Field(
        None, description="Field-specific error details if applicable"
    )


class SortInfo(BaseModel):
    """Represents sorting parameters applied to a list response.

    Used within `PaginationInfo` to indicate how the results are sorted.

    Attributes:
        property: The name of the field the results are sorted by.
        direction: The sort direction, typically "asc" (ascending) or "desc" (descending).
    """

    property: str = Field(
        ..., alias="property", description="The field to sort by"
    )  # Use alias 'property'
    direction: str = Field(..., description="The sort direction (asc or desc)")


class PaginationInfo(BaseModel):
    """Represents pagination details for list responses from the iMednet API.

    Included in the `ApiResponse` for endpoints that return lists of resources.

    Attributes:
        currentPage: The current page number (0-indexed).
        size: The number of items requested per page.
        totalElements: The total number of elements available across all pages.
        totalPages: The total number of pages available.
        sort: An optional list of `SortInfo` objects indicating the sorting applied.
    """

    currentPage: int = Field(
        ..., alias="currentPage", ge=0, description="Current page number (0-indexed)"
    )  # Use alias
    size: int = Field(..., ge=0, description="Number of items per page")
    totalElements: int = Field(
        ..., alias="totalElements", ge=0, description="Total number of elements across all pages"
    )  # Use alias
    totalPages: int = Field(
        ..., alias="totalPages", ge=0, description="Total number of pages"
    )  # Add totalPages based on mock data
    sort: Optional[List[SortInfo]] = Field(None, description="Sorting information applied")


class Metadata(BaseModel):
    """Represents the metadata included in every iMednet API response.

    Attributes:
        status: A string indicating the overall status of the response
                (e.g., "OK", "BAD_REQUEST").
        path: The API endpoint path that was requested.
        timestamp: A `datetime` object indicating when the response was generated.
        error: An optional `ErrorDetail` object containing error information if the
               request failed.
    """

    status: str = Field(..., description="Response status (OK, BAD_REQUEST, etc.)")
    path: Optional[str] = Field(None, description="The API endpoint path")
    timestamp: datetime = Field(..., description="Timestamp of the response")
    error: Optional[ErrorDetail] = Field(None, description="Error details if applicable")


class ApiResponse(BaseModel, Generic[T]):
    """A generic Pydantic model representing the standard iMednet API response structure.

    This model wraps the actual data payload (`data`) along with metadata and
    optional pagination information.

    Type Parameters:
        T: The type of the data payload contained within the response. This is often
           a `List` of resource-specific models (e.g., `List[StudyModel]`) or a
           single resource model.

    Attributes:
        metadata: A `Metadata` object containing common response information like
                  status, timestamp, and potential errors.
        pagination: An optional `PaginationInfo` object included for list endpoints.
        data: The main data payload of the response, with its type specified by `T`.
              This is `None` if the request fails or returns no data.
    """

    model_config = ConfigDict(
        populate_by_name=True, json_encoders={datetime: lambda dt: dt.isoformat()}
    )

    metadata: Metadata = Field(..., description="Response metadata")
    pagination: Optional[PaginationInfo] = Field(
        None, description="Pagination information if applicable"
    )  # Add top-level pagination
    data: Optional[T] = Field(None, description="Response data of generic type T")
