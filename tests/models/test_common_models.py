"""Tests for common data models."""

from datetime import datetime
from typing import Dict, List

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
    # Use the actual field name 'property' as defined in the model
    sort = SortInfo(property="dateCreated", direction="asc")
    assert sort.property == "dateCreated"
    assert sort.direction == "asc"  # Expect lowercase as provided

    # Test validation with alias 'field'
    sort_alias = SortInfo.model_validate({"property": "recordId", "direction": "DESC"})
    assert sort_alias.property == "recordId"
    assert sort_alias.direction == "DESC"


def test_pagination_info():
    """Test PaginationInfo model validation."""
    # Use actual field names
    pagination = PaginationInfo(currentPage=1, size=10, totalElements=100, totalPages=10)
    assert pagination.currentPage == 1
    assert pagination.size == 10
    assert pagination.totalElements == 100
    assert pagination.totalPages == 10

    # Test validation with aliases
    pagination_alias = PaginationInfo.model_validate(
        {"currentPage": 0, "size": 25, "totalElements": 5, "totalPages": 1}
    )
    assert pagination_alias.currentPage == 0
    assert pagination_alias.size == 25
    assert pagination_alias.totalElements == 5
    assert pagination_alias.totalPages == 1


def test_metadata():
    """Test Metadata model validation."""
    metadata = Metadata(
        status="OK",
        path="/api/v1/edc/studies",
        timestamp=datetime.now(),
        # pagination=pagination_data, # Metadata does not contain pagination
        error=None,
    )
    assert metadata.status == "OK"
    assert metadata.path == "/api/v1/edc/studies"
    assert isinstance(metadata.timestamp, datetime)
    assert metadata.error is None

    # Test with error
    # Use 'description' instead of 'message' for ErrorDetail
    error_detail = ErrorDetail(code="ERR001", description="Something went wrong")
    metadata_error = Metadata(
        status="ERROR",
        path="/api/v1/edc/studies",
        timestamp=datetime.now(),
        # pagination=None,
        error=error_detail,
    )
    assert metadata_error.status == "ERROR"
    assert metadata_error.error == error_detail


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


def test_api_response_no_pagination():
    """Test ApiResponse initialization when pagination is missing."""
    data = [{"id": 1, "name": "Test"}]
    response = ApiResponse[List[Dict]](data=data, pagination=None)
    assert response.data == data
    assert response.pagination is None
