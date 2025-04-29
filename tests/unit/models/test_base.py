import pytest
from imednet.models.base import ApiResponse, Error, Metadata, Pagination, SortField
from imednet.models.validators import parse_datetime
from pydantic import ValidationError

# Sample data for testing
SAMPLE_SORT_FIELD_DATA = {"property": "name", "direction": "ASC"}
SAMPLE_PAGINATION_DATA = {
    "currentPage": 1,
    "size": 10,
    "totalPages": 5,
    "totalElements": 42,
    "sort": [SAMPLE_SORT_FIELD_DATA],
}
SAMPLE_ERROR_DATA = {
    "code": "ERR001",
    "message": "Something went wrong",
    "details": {"field": "value"},
}
SAMPLE_METADATA_DATA = {
    "status": "SUCCESS",
    "method": "GET",
    "path": "/api/v1/items",
    "timestamp": "2023-10-27T10:00:00Z",
    "error": SAMPLE_ERROR_DATA,
}
SAMPLE_API_RESPONSE_DATA = {
    "metadata": SAMPLE_METADATA_DATA,
    "pagination": SAMPLE_PAGINATION_DATA,
    "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
}
SAMPLE_API_RESPONSE_DATA_NO_PAGINATION = {
    "metadata": SAMPLE_METADATA_DATA,
    "data": {"id": 1, "name": "Item 1"},
}
SAMPLE_API_RESPONSE_DATA_NO_ERROR = {
    "metadata": {
        "status": "SUCCESS",
        "method": "GET",
        "path": "/api/v1/items",
        "timestamp": "2023-10-27T10:00:00Z",
        # Error is omitted, should default
    },
    "data": {"id": 1, "name": "Item 1"},
}


def test_sort_field_creation():
    """Test SortField model creation from dictionary."""
    sort_field = SortField.model_validate(SAMPLE_SORT_FIELD_DATA)
    assert sort_field.property == "name"
    assert sort_field.direction == "ASC"


def test_sort_field_creation_with_none():
    """Test SortField creation with None values, expecting defaults."""
    sort_field = SortField.model_validate({"property": None, "direction": None})
    assert sort_field.property == ""  # Default from parse_str_or_default
    assert sort_field.direction == ""  # Default from parse_str_or_default


def test_pagination_creation():
    """Test Pagination model creation from dictionary."""
    pagination = Pagination.model_validate(SAMPLE_PAGINATION_DATA)
    assert pagination.current_page == 1
    assert pagination.size == 10
    assert pagination.total_pages == 5
    assert pagination.total_elements == 42
    assert len(pagination.sort) == 1
    assert pagination.sort[0].property == "name"


def test_pagination_creation_with_none():
    """Test Pagination creation with None values, expecting defaults."""
    pagination = Pagination.model_validate(
        {"currentPage": None, "size": None, "totalPages": None, "totalElements": None, "sort": None}
    )
    assert pagination.current_page == 0  # Default from parse_int_or_default
    assert pagination.size == 0  # Default from parse_int_or_default
    assert pagination.total_pages == 0  # Default from parse_int_or_default
    assert pagination.total_elements == 0  # Default from parse_int_or_default
    assert pagination.sort == []  # Default from parse_list_or_default


def test_error_creation():
    """Test Error model creation from dictionary."""
    error = Error.model_validate(SAMPLE_ERROR_DATA)
    assert error.code == "ERR001"
    assert error.message == "Something went wrong"
    assert error.details == {"field": "value"}


def test_error_creation_with_none():
    """Test Error creation with None values, expecting defaults."""
    error = Error.model_validate({"code": None, "message": None, "details": None})
    assert error.code == ""
    assert error.message == ""
    assert error.details == {}  # Validator handles None -> {}


def test_metadata_creation():
    """Test Metadata model creation from dictionary."""
    metadata = Metadata.model_validate(SAMPLE_METADATA_DATA)
    assert metadata.status == "SUCCESS"
    assert metadata.method == "GET"
    assert metadata.path == "/api/v1/items"
    assert metadata.timestamp == parse_datetime("2023-10-27T10:00:00Z")
    assert metadata.error.code == "ERR001"


def test_metadata_creation_no_error():
    """Test Metadata creation when error field is missing, expecting default Error."""
    metadata = Metadata.model_validate(
        {
            "status": "SUCCESS",
            "method": "GET",
            "path": "/api/v1/items",
            "timestamp": "2023-10-27T10:00:00Z",
        }
    )
    assert metadata.error is not None
    assert metadata.error.code == ""
    assert metadata.error.message == ""


def test_metadata_creation_with_none():
    """Test Metadata creation with None values, expecting defaults/errors."""
    # Timestamp is required, so None should raise validation error
    with pytest.raises(ValidationError):
        Metadata.model_validate(
            {
                "status": None,
                "method": None,
                "path": None,
                "timestamp": None,  # Required field
                "error": None,
            }
        )

    # Test with valid timestamp but other Nones (omit 'error' so default is used)
    metadata = Metadata.model_validate(
        {"status": None, "method": None, "path": None, "timestamp": "2023-10-27T10:00:00Z"}
    )
    assert metadata.status == ""
    assert metadata.method == ""
    assert metadata.path == ""
    assert metadata.timestamp == parse_datetime("2023-10-27T10:00:00Z")
    assert metadata.error is not None
    assert metadata.error.code == ""
    assert metadata.error.message == ""


def test_api_response_creation():
    """Test ApiResponse model creation with pagination."""
    response = ApiResponse[list].model_validate(SAMPLE_API_RESPONSE_DATA)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, Pagination)
    assert response.pagination.current_page == 1
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert response.data[0] == {"id": 1, "name": "Item 1"}


def test_api_response_creation_no_pagination():
    """Test ApiResponse model creation without pagination."""
    response = ApiResponse[dict].model_validate(SAMPLE_API_RESPONSE_DATA_NO_PAGINATION)
    assert isinstance(response.metadata, Metadata)
    assert response.pagination is None
    assert isinstance(response.data, dict)
    assert response.data == {"id": 1, "name": "Item 1"}


def test_api_response_creation_no_error_in_metadata():
    """Test ApiResponse creation where metadata lacks an error field."""
    response = ApiResponse[dict].model_validate(SAMPLE_API_RESPONSE_DATA_NO_ERROR)
    assert isinstance(response.metadata, Metadata)
    assert response.metadata.error is not None
    assert response.metadata.error.code == ""
    assert response.pagination is None
    assert isinstance(response.data, dict)
    assert response.data == {"id": 1, "name": "Item 1"}


def test_api_response_missing_required_fields():
    """Test ApiResponse creation fails when required fields are missing."""
    with pytest.raises(ValidationError):
        ApiResponse.model_validate({})  # Missing metadata and data

    with pytest.raises(ValidationError):
        ApiResponse.model_validate({"metadata": SAMPLE_METADATA_DATA})  # Missing data

    with pytest.raises(ValidationError):
        ApiResponse.model_validate({"data": {"id": 1}})  # Missing metadata
