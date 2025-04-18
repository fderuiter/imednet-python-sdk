"""Tests for common data models."""

from datetime import datetime
from typing import List

import pytest
from pydantic import ValidationError

from imednet_sdk.models._common import (ApiResponse, ErrorDetail, FieldError, Metadata,
                                        PaginationInfo, SortInfo)


def test_field_error():
    """Test FieldError model validation."""
    error = FieldError(attribute="page", value="XX")
    assert error.attribute == "page"
    assert error.value == "XX"


def test_error_detail():
    """Test ErrorDetail model validation."""
    error = ErrorDetail(
        code="1000",
        description="Field raised validation errors",
        field=FieldError(attribute="page", value="XX"),
    )
    assert error.code == "1000"
    assert error.description == "Field raised validation errors"
    assert error.field.attribute == "page"


def test_sort_info():
    """Test SortInfo model validation."""
    sort = SortInfo(field="dateCreated", direction="asc")
    assert sort.field == "dateCreated"
    assert sort.direction == "asc"


def test_pagination_info():
    """Test PaginationInfo model validation."""
    pagination = PaginationInfo(page=1, size=10, total=100)
    assert pagination.page == 1
    assert pagination.size == 10
    assert pagination.total == 100


def test_metadata():
    """Test Metadata model validation."""
    metadata = Metadata(
        status="OK",
        path="/api/v1/edc/studies",
        timestamp=datetime.now(),
        pagination=PaginationInfo(page=1, size=10, total=100),
    )
    assert metadata.status == "OK"
    assert metadata.path == "/api/v1/edc/studies"
    assert metadata.pagination.page == 1


def test_api_response():
    """Test ApiResponse model validation with different types."""
    # Test with a list of strings
    response = ApiResponse[List[str]](
        metadata=Metadata(status="OK", timestamp=datetime.now()), data=["item1", "item2"]
    )
    assert response.metadata.status == "OK"
    assert len(response.data) == 2
    assert "item1" in response.data


def test_error_response():
    """Test API error response."""
    error_response = ApiResponse[None](
        metadata=Metadata(
            status="BAD_REQUEST",
            path="/api/v1/edc/studies",
            timestamp=datetime.now(),
            error=ErrorDetail(
                code="1000",
                description="Field raised validation errors",
                field=FieldError(attribute="page", value="XX"),
            ),
        )
    )
    assert error_response.metadata.status == "BAD_REQUEST"
    assert error_response.metadata.error.code == "1000"
    assert error_response.data is None


def test_invalid_pagination():
    """Test invalid pagination values raise ValidationError."""
    with pytest.raises(ValidationError):
        PaginationInfo(page=-1, size=10, total=100)
