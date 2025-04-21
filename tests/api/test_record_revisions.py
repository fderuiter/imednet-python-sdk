"""Tests for the RecordRevisions API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.record_revisions import RecordRevisionsClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.models.record_revision import RecordRevisionModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
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
MOCK_REVISION_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "recordRevisionId": 5001,
    "recordId": 1001,
    "recordOid": "REC-001",
    "recordRevision": 1,
    "dataRevision": 1,
    "recordStatus": "In Progress",
    "subjectId": 50,
    "subjectOid": "SUBJ-001",
    "subjectKey": "S001",
    "siteId": 5,
    "formKey": "DEMOGRAPHICS",
    "intervalId": 1,
    "role": "Data Entry",
    "user": "user1",
    "reasonForChange": None,
    "deleted": False,
    "dateCreated": "2023-04-01T10:00:00Z",
}
MOCK_REVISION_2_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "recordRevisionId": 5002,
    "recordId": 1001,
    "recordOid": "REC-001",
    "recordRevision": 2,
    "dataRevision": 2,
    "recordStatus": "Complete",
    "subjectId": 50,
    "subjectOid": "SUBJ-001",
    "subjectKey": "S001",
    "siteId": 5,
    "formKey": "DEMOGRAPHICS",
    "intervalId": 1,
    "role": "Monitor",
    "user": "monitor1",
    "reasonForChange": "Corrected age",
    "deleted": False,
    "dateCreated": "2023-04-02T11:00:00Z",
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": REVISIONS_ENDPOINT,
    "timestamp": datetime.now().isoformat(),
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_REVISION_1_DICT, MOCK_REVISION_2_DICT],
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
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, RecordRevisionModel) for item in response.data)
    assert response.data[0].recordRevisionId == 5001
    assert response.data[1].recordRevisionId == 5002
    assert response.data[1].reasonForChange == "Corrected age"


@respx.mock
def test_list_record_revisions_with_params(revisions_client):
    """Test list_record_revisions with query parameters."""
    expected_params = {
        "page": "0",
        "size": "50",
        "sort": "recordId,asc",
        "filter": 'user=="user1"',
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{REVISIONS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Mock response content doesn't matter here
    )

    revisions_client.list_record_revisions(
        study_key=MOCK_STUDY_KEY,
        page=0,
        size=50,
        sort="recordId,asc",
        filter='user=="user1"',
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "0"
    assert request.url.params["size"] == "50"
    assert request.url.params["sort"] == "recordId,asc"
    assert request.url.params["filter"] == 'user=="user1"'


def test_list_record_revisions_no_study_key(revisions_client):
    """Test list_record_revisions raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        revisions_client.list_record_revisions(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        revisions_client.list_record_revisions(study_key=None)  # type: ignore
