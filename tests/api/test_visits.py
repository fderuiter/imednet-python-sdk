# Tests for the Visits API client.

from datetime import date, datetime  # Import date

import pytest
import respx
from httpx import Response

from imednet_sdk.api.visits import VisitsClient  # Import specific client
from imednet_sdk.client import ImednetClient
# Use PaginationInfo based on documentation structure
from imednet_sdk.models._common import (ApiResponse, Metadata, PaginationInfo,
                                        SortInfo)
from imednet_sdk.models.visit import VisitModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "PHARMADEMO"  # Use example from docs
VISITS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/visits"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def visits_client(client):
    """Fixture for VisitsClient."""
    return VisitsClient(client)


# --- Mock Data ---
# Corrected mock data based on docs/reference/visits.md example
MOCK_VISIT_1_DICT = {
    "visitId": 1,
    "studyKey": MOCK_STUDY_KEY,
    "intervalId": 13,
    "intervalName": "Day 15",
    "subjectId": 247,
    "subjectKey": "111-005",
    "startDate": "2024-11-04",  # Date only
    "endDate": "2024-11-11",  # Date only
    "dueDate": None,
    "visitDate": "2024-11-06",  # Date only
    "visitDateForm": "Follow Up",
    "deleted": False,
    "visitDateQuestion": "AESEV",
    "dateCreated": "2024-11-04 16:03:19",  # Datetime
    "dateModified": "2024-11-04 16:03:19",  # Datetime
}
# MOCK_VISIT_2_DICT can be added if needed

# Corrected Metadata based on docs
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": VISITS_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "visitId", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_VISIT_1_DICT],  # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_visits_success(visits_client):
    """Test successful listing of visits."""
    list_route = respx.get(f"{MOCK_BASE_URL}{VISITS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = visits_client.list_visits(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    # Assert pagination is present and correct type
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.metadata.status == "OK"
    assert response.metadata.path == VISITS_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "visitId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], VisitModel)
    # Assertions based on corrected mock data
    assert response.data[0].visitId == 1
    assert response.data[0].intervalId == 13
    assert response.data[0].intervalName == "Day 15"
    assert response.data[0].subjectKey == "111-005"
    assert response.data[0].visitDateForm == "Follow Up"
    assert response.data[0].visitDateQuestion == "AESEV"
    assert response.data[0].deleted is False
    # Check date/datetime parsing
    assert response.data[0].startDate == date.fromisoformat("2024-11-04")
    assert response.data[0].endDate == date.fromisoformat("2024-11-11")
    assert response.data[0].visitDate == date.fromisoformat("2024-11-06")
    assert response.data[0].dueDate is None
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")
    assert response.data[0].dateModified == datetime.fromisoformat("2024-11-04 16:03:19")


@respx.mock
def test_list_visits_with_params(visits_client):
    """Test listing visits with query parameters."""
    # Correct sort and filter syntax
    params = {"page": "2", "size": "5", "sort": "visitId,asc", "filter": "subjectKey==270"}
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{VISITS_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 2,
        "size": 5,
        "totalPages": 3,
        "totalElements": 14,
        "sort": [{"property": "visitId", "direction": "ASC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{VISITS_ENDPOINT}", params=params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = visits_client.list_visits(
        study_key=MOCK_STUDY_KEY, page=2, size=5, sort="visitId,asc", filter="subjectKey==270"
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "2"
    assert request.url.params["size"] == "5"
    assert request.url.params["sort"] == "visitId,asc"
    assert request.url.params["filter"] == "subjectKey==270"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.currentPage == 2
    assert response.pagination.size == 5
    assert response.pagination.sort[0].property == "visitId"
    assert response.pagination.sort[0].direction == "ASC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_visits_missing_study_key(visits_client):
    """Test listing visits with missing study_key raises ValueError."""
    # Match error message from client implementation
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        visits_client.list_visits(study_key="")

    with pytest.raises(ValueError, match="study_key cannot be empty"):
        visits_client.list_visits(study_key=None)  # type: ignore
