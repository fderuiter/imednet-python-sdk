"""Tests for the Studies API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.studies import StudiesClient
from imednet_sdk.client import ImednetClient
# Use PaginationInfo based on _common.py
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo, SortInfo
from imednet_sdk.models.study import StudyModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
STUDIES_ENDPOINT = "/api/v1/edc/studies"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def studies_client(client):
    """Fixture for StudiesClient."""
    return StudiesClient(client)


# --- Mock Data ---
# Corrected mock data based on docs/reference/studies.md example
MOCK_STUDY_1_DICT = {
    "sponsorKey": "100",
    "studyKey": "PHARMADEMO",
    "studyId": 100,
    "studyName": "iMednet Pharma Demonstration Study",
    "studyDescription": "iMednet Demonstration Study v2 Created 05April2018 After A5 Release",  # Added from docs
    "studyType": "STUDY",
    "dateCreated": "2024-11-04 16:03:18",  # Use format from docs
    "dateModified": "2024-11-04 16:03:19",
}
# MOCK_STUDY_2_DICT can be added if needed for multi-item tests

# Corrected Metadata based on docs
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": STUDIES_ENDPOINT,
    "timestamp": "2024-11-04 16:03:18",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "studyKey", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_STUDY_1_DICT],  # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_studies_success(studies_client, client):
    """Test successful retrieval of studies list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = studies_client.list_studies()

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], StudyModel)
    # Assertions based on corrected mock data
    assert response.data[0].studyKey == "PHARMADEMO"
    assert response.data[0].studyName == "iMednet Pharma Demonstration Study"
    assert (
        response.data[0].studyDescription
        == "iMednet Demonstration Study v2 Created 05April2018 After A5 Release"
    )
    assert response.data[0].studyType == "STUDY"
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:18")
    assert response.data[0].dateModified == datetime.fromisoformat("2024-11-04 16:03:19")

    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "studyKey"
    assert response.pagination.sort[0].direction == "ASC"


@respx.mock
def test_list_studies_with_params(studies_client, client):
    """Test retrieving studies list with pagination, sort, and filter."""
    # Use filter syntax from docs example (==)
    params = {"page": 1, "size": 10, "sort": "studyKey,desc", "filter": "studyKey==PHARMADEMO"}

    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{STUDIES_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 1,
        "size": 10,
        "totalPages": 1,
        "totalElements": 0,
        "sort": [{"property": "studyKey", "direction": "DESC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    # Let respx match based on params dictionary
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}", params=params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = studies_client.list_studies(**params)

    assert list_route.called
    request = list_route.calls.last.request
    # Verify parameters were sent correctly
    assert request.url.params["page"] == "1"
    assert request.url.params["size"] == "10"
    assert request.url.params["sort"] == "studyKey,desc"
    assert request.url.params["filter"] == "studyKey==PHARMADEMO"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.currentPage == 1  # Correct assertion to match requested page
    assert response.pagination.size == 10
    assert response.pagination.sort[0].property == "studyKey"
    assert response.pagination.sort[0].direction == "DESC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


@respx.mock
def test_list_studies_empty_response(studies_client):
    """Test retrieving an empty list of studies."""
    # Correct pagination model
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{STUDIES_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 0,
        "size": 25,
        "totalPages": 0,
        "totalElements": 0,
        "sort": [{"property": "studyKey", "direction": "ASC"}],
    }
    empty_response_dict = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(200, json=empty_response_dict)
    )

    response = studies_client.list_studies()

    assert list_route.called
    assert response is not None
    assert isinstance(response.data, list)
    assert len(response.data) == 0
    # Assert pagination details
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.totalElements == 0
    assert response.pagination.totalPages == 0


# Note: Tests for error handling (e.g., 4xx/5xx responses)
# will be added as part of Task 06 (Error Handling and Exceptions).
