"""Tests for common data models."""

from datetime import datetime
from typing import List

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from imednet_sdk.models._common import (ApiResponse, ErrorDetail, FieldError, Metadata,
                                        PaginationInfo, SortInfo)


# --- Helper Dummy Model for Generic Tests ---
class DummyDataModel(BaseModel):
    id: int
    value: str


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


# --- Tests for Generic ApiResponse with TypeAdapter ---

VALID_METADATA_DICT = {
    "status": "OK",
    "path": "/api/v1/dummy",
    "timestamp": datetime.now().isoformat(),  # Use ISO format for JSON compatibility
}

VALID_DUMMY_DATA_SINGLE_DICT = {"id": 1, "value": "test"}

VALID_DUMMY_DATA_LIST_DICT = [{"id": 1, "value": "test1"}, {"id": 2, "value": "test2"}]

VALID_API_RESPONSE_SINGLE_DICT = {
    "metadata": VALID_METADATA_DICT,
    "data": VALID_DUMMY_DATA_SINGLE_DICT,
}

VALID_API_RESPONSE_LIST_DICT = {"metadata": VALID_METADATA_DICT, "data": VALID_DUMMY_DATA_LIST_DICT}


def test_api_response_typeadapter_single():
    """Test validating ApiResponse[DummyDataModel] using TypeAdapter."""
    adapter = TypeAdapter(ApiResponse[DummyDataModel])
    validated_response = adapter.validate_python(VALID_API_RESPONSE_SINGLE_DICT)

    assert isinstance(validated_response, ApiResponse)
    assert isinstance(validated_response.metadata, Metadata)
    assert validated_response.metadata.status == "OK"
    assert isinstance(validated_response.data, DummyDataModel)
    assert validated_response.data.id == 1
    assert validated_response.data.value == "test"


def test_api_response_typeadapter_list():
    """Test validating ApiResponse[List[DummyDataModel]] using TypeAdapter."""
    adapter = TypeAdapter(ApiResponse[List[DummyDataModel]])
    validated_response = adapter.validate_python(VALID_API_RESPONSE_LIST_DICT)

    assert isinstance(validated_response, ApiResponse)
    assert isinstance(validated_response.metadata, Metadata)
    assert validated_response.metadata.status == "OK"
    assert isinstance(validated_response.data, list)
    assert len(validated_response.data) == 2
    assert all(isinstance(item, DummyDataModel) for item in validated_response.data)
    assert validated_response.data[0].id == 1
    assert validated_response.data[1].id == 2


def test_api_response_typeadapter_validation_error_data():
    """Test TypeAdapter raises ValidationError for invalid data within ApiResponse."""
    adapter = TypeAdapter(ApiResponse[DummyDataModel])
    invalid_data = VALID_API_RESPONSE_SINGLE_DICT.copy()
    invalid_data["data"] = {"id": "not-an-int", "value": "test"}  # Invalid id type

    with pytest.raises(ValidationError) as excinfo:
        adapter.validate_python(invalid_data)

    # Check the error message points to the nested data field
    assert "data.id" in str(excinfo.value)


def test_api_response_typeadapter_validation_error_metadata():
    """Test TypeAdapter raises ValidationError for invalid metadata within ApiResponse."""
    adapter = TypeAdapter(ApiResponse[DummyDataModel])
    invalid_data = VALID_API_RESPONSE_SINGLE_DICT.copy()
    invalid_data["metadata"] = {"status": "OK"}  # Missing required timestamp

    with pytest.raises(ValidationError) as excinfo:
        adapter.validate_python(invalid_data)

    # Check the error message points to the nested metadata field
    assert "metadata.timestamp" in str(excinfo.value)
