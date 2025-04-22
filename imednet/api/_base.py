"""
Base class and common Pydantic models for the iMednet SDK.

This module provides:

- `ResourceClient`: foundation for all resource-specific API clients (e.g., StudiesClient).
- Common Pydantic models for API responses:
  - `FieldError`, `ErrorDetail`, `SortInfo`, `PaginationInfo`, `Metadata`, `ApiResponse`.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import httpx
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from imednet_sdk.client import ImednetClient, TimeoutTypes

# Type variable for ResourceClient response models
R = TypeVar("R", bound=BaseModel)


class ResourceClient:
    """Base class for specific iMednet API resource endpoint clients.

    Provides `_get` and `_post` helper methods that delegate to the main
    `ImednetClient._request` method. Subclasses (e.g., StudiesClient)
    call these to implement resource-specific operations.
    """

    def __init__(self, client: ImednetClient):
        """Initialize with a reference to the main `ImednetClient`."""
        self._client = client

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Union[Type[R], Type[List[R]]]] = None,
        timeout: Optional[TimeoutTypes] = None,
        **kwargs: Any,
    ) -> Union[R, List[R], httpx.Response]:
        """Send a GET request via the main `ImednetClient`."""
        return self._client._request(
            "GET", endpoint, params=params, response_model=response_model, timeout=timeout, **kwargs
        )

    def _post(
        self,
        endpoint: str,
        json: Optional[Any] = None,
        response_model: Optional[Union[Type[R], Type[List[R]]]] = None,
        timeout: Optional[TimeoutTypes] = None,
        **kwargs: Any,
    ) -> Union[R, List[R], httpx.Response]:
        """Send a POST request via the main `ImednetClient`."""
        return self._client._request(
            "POST", endpoint, json=json, response_model=response_model, timeout=timeout, **kwargs
        )


# Common Pydantic models


class FieldError(BaseModel):
    """Details about an error related to a specific request field."""

    attribute: str = Field(..., description="The request attribute that caused the error")
    value: str = Field(..., description="The invalid value provided for the problematic attribute")


class ErrorDetail(BaseModel):
    """Structured error information returned by the iMednet API."""

    code: Optional[str] = Field(None, description="Error code representing the error type")
    description: Optional[str] = Field(None, description="Human-readable description of the error")
    field: Optional[FieldError] = Field(
        None, description="Field-specific error details if applicable"
    )


class SortInfo(BaseModel):
    """Sorting parameters applied to a list response."""

    property: str = Field(..., alias="property", description="The field to sort by")
    direction: str = Field(..., description="Sort direction, 'asc' or 'desc'")


class PaginationInfo(BaseModel):
    """Pagination details for list responses."""

    currentPage: int = Field(
        ..., alias="currentPage", ge=0, description="Current page number (0-indexed)"
    )
    size: int = Field(..., ge=0, description="Number of items per page")
    totalElements: int = Field(
        ..., alias="totalElements", ge=0, description="Total number of elements"
    )
    totalPages: int = Field(..., alias="totalPages", ge=0, description="Total number of pages")
    sort: Optional[List[SortInfo]] = Field(None, description="Sorting information applied")


class Metadata(BaseModel):
    """Metadata included in every iMednet API response."""

    status: str = Field(..., description="Response status (e.g., 'OK', 'BAD_REQUEST')")
    path: Optional[str] = Field(None, description="The API endpoint path")
    timestamp: datetime = Field(..., description="Timestamp when the response was generated")
    error: Optional[ErrorDetail] = Field(None, description="Error details if the request failed")


# Type variable for generic ApiResponse
T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Generic model representing the standard iMednet API response structure."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda dt: dt.isoformat()},
    )

    metadata: Metadata = Field(..., description="Response metadata")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination info if applicable")
    data: Optional[T] = Field(None, description="The main data payload of type T")
