"""Tests for the Intervals API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.intervals import IntervalsClient
from imednet_sdk.client import ImednetClient
# Use Pagination and SortInfo based on documentation structure
from imednet_sdk.models._common import ApiResponse, Metadata, Pagination, SortInfo
from imednet_sdk.models.interval import IntervalFormModel, IntervalModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
INTERVALS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/intervals"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def intervals_client(client):
    """Fixture for IntervalsClient."""
    return IntervalsClient(client)


# --- Mock Data ---
MOCK_INTERVAL_FORM_1 = {
    "formId": 123,  # Use example from docs
    "formKey": "MY-FORM-KEY",
    "formName": "myFormName",
}
# MOCK_INTERVAL_FORM_2 can be removed or updated if needed for other tests

MOCK_INTERVAL_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "intervalId": 1,
    "intervalName": "Day 1",  # Use example from docs
    "intervalDescription": "Day 1",
    "intervalSequence": 110,
    "intervalGroupId": 10,
    "intervalGroupName": "ePRO",
    "timeline": "Start Date End Date",
    "definedUsingInterval": "Baseline",
    "windowCalculationForm": "Procedure",
    "windowCalculationDate": "PROCDT",
    "actualDateForm": "Follow Up",
    "actualDate": "FUDT",
    "dueDateWillBeIn": 30,
    "negativeSlack": 7,
    "positiveSlack": 7,
    "eproGracePeriod": 2,
    "forms": [MOCK_INTERVAL_FORM_1],
    "disabled": True,  # Match example
    "dateCreated": "2024-11-04 16:03:19",  # Use format from docs
    "dateModified": "2024-11-04 16:03:20",
}
# MOCK_INTERVAL_2_DICT can be removed or updated if needed for other tests

# Corrected Metadata based on docs (no nested pagination)
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": INTERVALS_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "intervalId", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_INTERVAL_1_DICT],  # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_intervals_success(intervals_client):
    """Test successful retrieval of intervals list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{INTERVALS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = intervals_client.list_intervals(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    # Assert pagination is present and correct type
    assert isinstance(response.pagination, Pagination)
    assert response.metadata.status == "OK"
    assert response.metadata.path == INTERVALS_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "intervalId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], IntervalModel)
    assert response.data[0].intervalName == "Day 1"
    assert response.data[0].disabled is True
    assert isinstance(response.data[0].forms, list)
    assert len(response.data[0].forms) == 1
    assert isinstance(response.data[0].forms[0], IntervalFormModel)
    assert response.data[0].forms[0].formKey == "MY-FORM-KEY"
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")


@respx.mock
def test_list_intervals_with_params(intervals_client):
    """Test list_intervals with query parameters."""
    # Use filter syntax from docs example (==)
    params = {
        "page": 2,
        "size": 5,
        "sort": "intervalSequence,desc",
        "filter": "intervalGroupName==ePRO",  # Use == as per docs
    }
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{INTERVALS_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 2,
        "size": 5,
        "totalPages": 3,
        "totalElements": 12,
        "sort": [{"property": "intervalSequence", "direction": "DESC"}],
    }
    # Example: return empty data for this specific filter/page
    mock_response = {"metadata": mock_metadata, "pagination": mock_pagination, "data": []}

    # Ensure respx matches the exact params
    expected_params = {
        "page": "2",
        "size": "5",
        "sort": "intervalSequence,desc",
        "filter": "intervalGroupName==ePRO",
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{INTERVALS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = intervals_client.list_intervals(
        study_key=MOCK_STUDY_KEY,
        page=2,
        size=5,
        sort="intervalSequence,desc",
        filter="intervalGroupName==ePRO",
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "2"
    assert request.url.params["size"] == "5"
    assert request.url.params["sort"] == "intervalSequence,desc"
    assert request.url.params["filter"] == "intervalGroupName==ePRO"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, Pagination)
    assert response.pagination.currentPage == 2
    assert response.pagination.size == 5
    assert response.pagination.sort[0].property == "intervalSequence"
    assert response.pagination.sort[0].direction == "DESC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_intervals_no_study_key(intervals_client):
    """Test list_intervals raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        intervals_client.list_intervals(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        intervals_client.list_intervals(study_key=None)  # type: ignore
