"""Tests for the Subjects API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.subjects import SubjectsClient
from imednet_sdk.client import ImednetClient
# Use Pagination and SortInfo based on documentation structure
from imednet_sdk.models._common import ApiResponse, Metadata, Pagination, SortInfo
# KeywordModel is defined in record.py now
from imednet_sdk.models.record import KeywordModel
from imednet_sdk.models.subject import SubjectModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "PHARMADEMO"  # Use example from docs
SUBJECTS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/subjects"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def subjects_client(client):
    """Fixture for SubjectsClient."""
    return SubjectsClient(client)


# --- Mock Data ---
# Corrected Keyword based on docs example
MOCK_KEYWORD_1 = {
    "keywordName": "Data Entry Error",
    "keywordKey": "DEE",
    "keywordId": 15362,
    "dateAdded": "2024-11-04 16:03:19",
}
# MOCK_KEYWORD_2 can be removed or updated if needed

# Corrected mock data based on docs/reference/subjects.md example
MOCK_SUBJECT_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "subjectId": 1,
    "subjectOid": "OID-1",
    "subjectKey": "01-001",
    "subjectStatus": "Enrolled",
    "siteId": 128,
    "siteName": "Chicago Hope Hospital",
    "deleted": False,
    "enrollmentStartDate": "2024-11-04 16:03:19",  # Use format from docs
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
    "keywords": [MOCK_KEYWORD_1],
}
# MOCK_SUBJECT_2_DICT can be removed or updated if needed

# Corrected Metadata based on docs
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": SUBJECTS_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "subjectId", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_SUBJECT_1_DICT],  # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_subjects_success(subjects_client):
    """Test successful retrieval of subjects list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{SUBJECTS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = subjects_client.list_subjects(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    # Assert pagination is present and correct type
    assert isinstance(response.pagination, Pagination)
    assert response.metadata.status == "OK"
    assert response.metadata.path == SUBJECTS_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "subjectId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], SubjectModel)
    # Assertions based on corrected mock data
    assert response.data[0].subjectId == 1
    assert response.data[0].subjectKey == "01-001"
    assert response.data[0].siteName == "Chicago Hope Hospital"
    assert response.data[0].subjectStatus == "Enrolled"
    assert response.data[0].deleted is False
    assert response.data[0].enrollmentStartDate == datetime.fromisoformat("2024-11-04 16:03:19")
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")
    assert response.data[0].dateModified == datetime.fromisoformat("2024-11-04 16:03:20")

    assert isinstance(response.data[0].keywords, list)
    assert len(response.data[0].keywords) == 1
    assert isinstance(response.data[0].keywords[0], KeywordModel)
    assert response.data[0].keywords[0].keywordName == "Data Entry Error"
    assert response.data[0].keywords[0].dateAdded == datetime.fromisoformat("2024-11-04 16:03:19")


@respx.mock
def test_list_subjects_with_params(subjects_client):
    """Test list_subjects with query parameters."""
    # Use filter syntax from docs example (==)
    expected_params = {
        "page": "0",
        "size": "25",
        "sort": "subjectId,ASC",
        "filter": "subjectId==370",  # Use == as per docs example
    }
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{SUBJECTS_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 0,
        "size": 25,
        "totalPages": 0,
        "totalElements": 0,
        "sort": [{"property": "subjectId", "direction": "ASC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{SUBJECTS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = subjects_client.list_subjects(
        study_key=MOCK_STUDY_KEY,
        page=0,
        size=25,
        sort="subjectId,ASC",
        filter="subjectId==370",
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "0"
    assert request.url.params["size"] == "25"
    assert request.url.params["sort"] == "subjectId,ASC"
    assert request.url.params["filter"] == "subjectId==370"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, Pagination)
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 25
    assert response.pagination.sort[0].property == "subjectId"
    assert response.pagination.sort[0].direction == "ASC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_subjects_no_study_key(subjects_client):
    """Test list_subjects raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        subjects_client.list_subjects(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        subjects_client.list_subjects(study_key=None)  # type: ignore
