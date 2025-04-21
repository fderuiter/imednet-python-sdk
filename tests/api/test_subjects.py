"""Tests for the Subjects API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.subjects import SubjectsClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.models.subject import KeywordModel, SubjectModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
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
MOCK_KEYWORD_1 = {
    "keywordName": "Screened",
    "keywordKey": "KW_SCREENED",
    "keywordId": 1,
    "dateAdded": "2023-07-01T10:00:00Z",
}
MOCK_KEYWORD_2 = {
    "keywordName": "Randomized",
    "keywordKey": "KW_RAND",
    "keywordId": 2,
    "dateAdded": "2023-07-05T11:00:00Z",
}

MOCK_SUBJECT_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "subjectId": 101,
    "subjectOid": "SUBJ-001",
    "subjectKey": "S001",
    "subjectStatus": "Enrolled",
    "siteId": 5,
    "siteName": "Site A",
    "enrollmentStartDate": "2023-07-01T09:00:00Z",
    "deleted": False,
    "dateCreated": "2023-07-01T08:00:00Z",
    "dateModified": "2023-07-02T14:00:00Z",
    "keywords": [MOCK_KEYWORD_1, MOCK_KEYWORD_2],
}
MOCK_SUBJECT_2_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "subjectId": 102,
    "subjectOid": "SUBJ-002",
    "subjectKey": "S002",
    "subjectStatus": "Screen Failed",
    "siteId": 6,
    "siteName": "Site B",
    "enrollmentStartDate": "2023-07-03T10:00:00Z",
    "deleted": False,
    "dateCreated": "2023-07-03T09:30:00Z",
    "dateModified": "2023-07-03T15:00:00Z",
    "keywords": [MOCK_KEYWORD_1],
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": SUBJECTS_ENDPOINT,
    "timestamp": datetime.now().isoformat(),
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_SUBJECT_1_DICT, MOCK_SUBJECT_2_DICT],
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
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, SubjectModel) for item in response.data)
    assert response.data[0].subjectKey == "S001"
    assert response.data[1].subjectKey == "S002"
    assert isinstance(response.data[0].keywords, list)
    assert len(response.data[0].keywords) == 2
    assert isinstance(response.data[0].keywords[0], KeywordModel)
    assert response.data[0].keywords[0].keywordName == "Screened"
    assert response.data[1].keywords[0].keywordName == "Screened"


@respx.mock
def test_list_subjects_with_params(subjects_client):
    """Test list_subjects with query parameters."""
    expected_params = {
        "page": "0",
        "size": "1",
        "sort": "enrollmentStartDate,desc",
        "filter": 'subjectStatus=="Enrolled"',
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{SUBJECTS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Mock response content doesn't matter here
    )

    subjects_client.list_subjects(
        study_key=MOCK_STUDY_KEY,
        page=0,
        size=1,
        sort="enrollmentStartDate,desc",
        filter='subjectStatus=="Enrolled"',
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "0"
    assert request.url.params["size"] == "1"
    assert request.url.params["sort"] == "enrollmentStartDate,desc"
    assert request.url.params["filter"] == 'subjectStatus=="Enrolled"'


def test_list_subjects_no_study_key(subjects_client):
    """Test list_subjects raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        subjects_client.list_subjects(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        subjects_client.list_subjects(study_key=None)  # type: ignore
