# filepath: /Users/fred/Documents/GitHub/imednet-python-sdk/tests/api/test_studies.py
"""Tests for the Studies API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

# Import the client we are testing
from imednet_sdk.api.studies import StudiesClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.models.study import StudyModel


@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    # We don't need real credentials for mocked tests
    return ImednetClient(
        username="testuser", password="testpassword", instance_subdomain="testinstance"
    )


@pytest.fixture
def studies_client(client):
    """Fixture for StudiesClient, directly instantiated for now."""
    # Directly instantiate StudiesClient for isolated testing
    # Later, this might use client.studies once integrated
    return StudiesClient(client)


# --- Mock Data ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
STUDIES_ENDPOINT = "/api/v1/edc/studies"

MOCK_STUDY_1_DICT = {
    "studyKey": "DEMO",
    "studyName": "Demonstration Study",
    "studyStatus": "Active",
    "dateCreated": "2023-01-15T10:00:00Z",
    "dateUpdated": "2023-01-16T11:30:00Z",
    "userCreated": "creator",
    "userUpdated": "updater",
}
MOCK_STUDY_2_DICT = {
    "studyKey": "PROD",
    "studyName": "Production Study",
    "studyStatus": "Active",
    "dateCreated": "2022-11-01T09:00:00Z",
    "dateUpdated": "2023-02-20T15:45:00Z",
    "userCreated": "admin",
    "userUpdated": "admin",
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": STUDIES_ENDPOINT,
    "timestamp": datetime.now().isoformat(),  # Dynamic timestamp
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_STUDY_1_DICT, MOCK_STUDY_2_DICT],
}


# --- Test Cases ---


@respx.mock
def test_list_studies_success(studies_client):
    """Test successful retrieval of studies list."""
    # Mock the API call
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    # Call the method
    response = studies_client.list_studies()

    # Assertions
    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    # We don't assert exact pagination numbers from mock if they can vary
    # assert response.metadata.pagination.page == 0
    # assert response.metadata.pagination.size == 2
    # assert response.metadata.pagination.total == 2
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(s, StudyModel) for s in response.data)
    assert response.data[0].study_key == "DEMO"
    assert response.data[1].study_key == "PROD"
    assert response.data[0].study_name == "Demonstration Study"
    # Check date parsing
    assert isinstance(response.data[0].date_created, datetime)
    assert response.data[0].date_created.year == 2023


@respx.mock
def test_list_studies_with_params(studies_client):
    """Test retrieving studies list with pagination, sort, and filter."""
    params = {"page": 1, "size": 10, "sort": "studyKey,desc", "filter": 'studyStatus=="Active"'}
    # httpx automatically URL-encodes parameters
    expected_url = f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}?page=1&size=10&sort=studyKey%2Cdesc&filter=studyStatus%3D%3D%22Active%22"

    # Mock the API call with specific query params
    # Use url__eq to ensure exact URL match including params
    list_route = respx.get(url=expected_url).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Using same mock data for simplicity
    )

    # Call the method with parameters
    response = studies_client.list_studies(**params)

    # Assertions
    assert list_route.called
    assert response is not None  # Basic check that response is received
    assert len(response.data) == 2  # Check data is parsed


@respx.mock
def test_list_studies_empty_response(studies_client):
    """Test retrieving an empty list of studies."""
    empty_response_dict = {
        "metadata": {
            "status": "OK",
            "path": STUDIES_ENDPOINT,
            "timestamp": datetime.now().isoformat(),
            "pagination": {"page": 0, "size": 25, "total": 0},
        },
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
    assert response.metadata.pagination.total == 0


# Note: Tests for error handling (e.g., 4xx/5xx responses)
# will be added as part of Task 06 (Error Handling and Exceptions).
