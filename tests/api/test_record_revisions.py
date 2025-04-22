"""Tests for the RecordRevisions API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.record_revisions import RecordRevisionsClient
from imednet_sdk.client import ImednetClient
# Use PaginationInfo based on _common.py
from imednet_sdk.models._common import (ApiResponse, Metadata, PaginationInfo,
                                        SortInfo)
from imednet_sdk.models.record_revision import RecordRevisionModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "PHARMADEMO"  # Use example from docs
REVISIONS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/recordRevisions"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def revisions_client(client):
    """Fixture for RecordRevisionsClient."""
    return RecordRevisionsClient(client)


# --- Mock Data ---
# Corrected mock data based on docs/reference/record_revisions.md example
MOCK_REVISION_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "recordRevisionId": 1,
    "recordId": 1,
    "recordOid": "REC-1",
    "recordRevision": 1,
    "dataRevision": 1,
    "recordStatus": "Record Complete",
    "subjectId": 247,
    "subjectOid": "OID-1",
    "subjectKey": "001-003",
    "siteId": 2,
    "formKey": "AE",
    "intervalId": 15,
    "role": "Research Coordinator",
    "user": "jdoe",
    "reasonForChange": "Data entry error",
    "deleted": True,
    "dateCreated": "2024-11-04 16:03:19",  # Use format from docs
}
# MOCK_REVISION_2_DICT can be removed or updated if needed for other tests

# Corrected Metadata based on docs (no nested pagination)
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": REVISIONS_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "recordRevisionId", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_REVISION_1_DICT],  # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_record_revisions_success(revisions_client):
    """Test successful retrieval of record revisions list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{REVISIONS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = revisions_client.list_record_revisions(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert isinstance(response.data, list)
    # Assert pagination is present and correct type
    assert response.metadata.status == "OK"
    assert response.metadata.path == REVISIONS_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "recordRevisionId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], RecordRevisionModel)
    # Assertions based on corrected mock data
    assert response.data[0].recordRevisionId == 1
    assert response.data[0].recordId == 1
    assert response.data[0].subjectKey == "001-003"
    assert response.data[0].user == "jdoe"
    assert response.data[0].reasonForChange == "Data entry error"
    assert response.data[0].deleted is True
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")


@respx.mock
def test_list_record_revisions_with_params(revisions_client):
    """Test list_record_revisions with query parameters."""
    # Use filter syntax from docs example (==)
    expected_params = {
        "page": "0",
        "size": "50",
        "sort": "recordId,asc",
        "filter": "subjectKey==270",  # Use == as per docs example
    }
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{REVISIONS_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 0,
        "size": 50,
        "totalPages": 0,
        "totalElements": 0,
        "sort": [{"property": "recordId", "direction": "ASC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{REVISIONS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = revisions_client.list_record_revisions(
        study_key=MOCK_STUDY_KEY,
        page=0,
        size=50,
        sort="recordId,asc",
        filter="subjectKey==270",
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "0"
    assert request.url.params["size"] == "50"
    assert request.url.params["sort"] == "recordId,asc"
    assert request.url.params["filter"] == "subjectKey==270"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 50
    assert response.pagination.sort[0].property == "recordId"
    assert response.pagination.sort[0].direction == "ASC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_record_revisions_no_study_key(revisions_client):
    """Test list_record_revisions raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        revisions_client.list_record_revisions(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        revisions_client.list_record_revisions(study_key=None)  # type: ignore
