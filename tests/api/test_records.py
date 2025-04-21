"""Tests for the Records API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.records import RecordsClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.models.record import RecordModel
from imednet_sdk.models.subject import KeywordModel  # Assuming KeywordModel is needed

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
RECORDS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/records"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def records_client(client):
    """Fixture for RecordsClient."""
    return RecordsClient(client)


# --- Mock Data ---
MOCK_KEYWORD_1 = {"keywordId": 1, "keywordName": "Screening"}
MOCK_KEYWORD_2 = {"keywordId": 2, "keywordName": "AE"}

MOCK_RECORD_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "intervalId": 1,
    "formId": 101,
    "formKey": "DEMOGRAPHICS",
    "siteId": 5,
    "recordId": 1001,
    "recordOid": "REC-001",
    "recordType": "Subject",
    "recordStatus": "Complete",
    "subjectId": 50,
    "subjectOid": "SUBJ-001",
    "subjectKey": "S001",
    "visitId": 201,
    "parentRecordId": None,
    "deleted": False,
    "dateCreated": "2023-04-01T10:00:00Z",
    "dateModified": "2023-04-02T11:00:00Z",
    "keywords": [MOCK_KEYWORD_1],
    "recordData": {"AGE": 35, "SEX": "Female"},
}
MOCK_RECORD_2_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "intervalId": 2,
    "formId": 102,
    "formKey": "ADVERSE_EVENTS",
    "siteId": 5,
    "recordId": 1002,
    "recordOid": "REC-002",
    "recordType": "Subject",
    "recordStatus": "In Progress",
    "subjectId": 50,
    "subjectOid": "SUBJ-001",
    "subjectKey": "S001",
    "visitId": 202,
    "parentRecordId": 1001,
    "deleted": False,
    "dateCreated": "2023-04-05T09:00:00Z",
    "dateModified": "2023-04-06T14:30:00Z",
    "keywords": [MOCK_KEYWORD_2],
    "recordData": {"AE_TERM": "Headache", "SEVERITY": "Mild"},
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": RECORDS_ENDPOINT,
    "timestamp": datetime.now().isoformat(),
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_RECORD_1_DICT, MOCK_RECORD_2_DICT],
}


# --- Test Cases ---
@respx.mock
def test_list_records_success(records_client):
    """Test successful retrieval of records list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{RECORDS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = records_client.list_records(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, RecordModel) for item in response.data)
    assert response.data[0].recordOid == "REC-001"
    assert response.data[1].recordOid == "REC-002"
    assert isinstance(response.data[0].keywords, list)
    assert len(response.data[0].keywords) == 1
    assert isinstance(response.data[0].keywords[0], KeywordModel)
    assert response.data[0].keywords[0].keywordName == "Screening"
    assert isinstance(response.data[0].recordData, dict)
    assert response.data[0].recordData["AGE"] == 35


@respx.mock
def test_list_records_with_params(records_client):
    """Test list_records with query parameters."""
    expected_params = {
        "page": "1",
        "size": "10",
        "sort": "dateCreated,desc",
        "filter": 'recordStatus=="Complete"',
        "recordDataFilter": "AGE>30",
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{RECORDS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Mock response content doesn't matter here
    )

    records_client.list_records(
        study_key=MOCK_STUDY_KEY,
        page=1,
        size=10,
        sort="dateCreated,desc",
        filter='recordStatus=="Complete"',
        record_data_filter="AGE>30",
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "1"
    assert request.url.params["size"] == "10"
    assert request.url.params["sort"] == "dateCreated,desc"
    assert request.url.params["filter"] == 'recordStatus=="Complete"'
    assert request.url.params["recordDataFilter"] == "AGE>30"


def test_list_records_no_study_key(records_client):
    """Test list_records raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        records_client.list_records(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        records_client.list_records(study_key=None)  # type: ignore
