"""Tests for the Sites API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.sites import SitesClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, Pagination, SortInfo
from imednet_sdk.models.site import SiteModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "PHARMADEMO"  # Use example from docs
SITES_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/sites"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def sites_client(client):
    """Fixture for SitesClient."""
    return SitesClient(client)


# --- Mock Data ---
# Corrected mock data based on docs/reference/sites.md example
MOCK_SITE_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "siteId": 1,
    "siteName": "Mock Site 1",
    "siteEnrollmentStatus": "Enrollment Open",
    "dateCreated": "2024-11-04 16:03:19",  # Use format from docs
    "dateModified": "2024-11-04 16:03:20",
}
# MOCK_SITE_2_DICT can be added if needed for multi-item tests

# Corrected Metadata based on docs (no nested pagination)
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": SITES_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "siteId", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_SITE_1_DICT],  # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_sites_success(sites_client):
    """Test successful retrieval of sites list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{SITES_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = sites_client.list_sites(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    # Assert pagination is present and correct type
    assert isinstance(response.pagination, Pagination)
    assert response.metadata.status == "OK"
    assert response.metadata.path == SITES_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "siteId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], SiteModel)
    # Assertions based on corrected mock data
    assert response.data[0].siteId == 1
    assert response.data[0].siteName == "Mock Site 1"
    assert response.data[0].siteEnrollmentStatus == "Enrollment Open"
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")
    assert response.data[0].dateModified == datetime.fromisoformat("2024-11-04 16:03:20")


@respx.mock
def test_list_sites_with_params(sites_client):
    """Test list_sites with query parameters."""
    # Use filter syntax from docs example (==)
    expected_params = {
        "page": "0",
        "size": "25",
        "sort": "siteId,ASC",
        "filter": "siteId==48",  # Use == as per docs example
    }
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{SITES_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 0,
        "size": 25,
        "totalPages": 0,
        "totalElements": 0,
        "sort": [{"property": "siteId", "direction": "ASC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{SITES_ENDPOINT}", params=expected_params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = sites_client.list_sites(
        study_key=MOCK_STUDY_KEY,
        page=0,
        size=25,
        sort="siteId,ASC",
        filter="siteId==48",
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "0"
    assert request.url.params["size"] == "25"
    assert request.url.params["sort"] == "siteId,ASC"
    assert request.url.params["filter"] == "siteId==48"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, Pagination)
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 25
    assert response.pagination.sort[0].property == "siteId"
    assert response.pagination.sort[0].direction == "ASC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_sites_no_study_key(sites_client):
    """Test list_sites raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        sites_client.list_sites(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        sites_client.list_sites(study_key=None)  # type: ignore
