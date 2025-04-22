"""Tests for the Records API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.records import RecordsClient
from imednet_sdk.client import ImednetClient

# Use PaginationInfo based on _common.py
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo, SortInfo
from imednet_sdk.models.job import JobStatusModel
from imednet_sdk.models.record import RecordModel, RecordPostItem

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "PHARMADEMO"  # Use example from docs
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
MOCK_RECORD_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "intervalId": 99,  # Use example from docs
    "formId": 10202,
    "formKey": "AE",
    "siteId": 128,
    "recordId": 1,
    "recordOid": "REC-1",
    "recordType": "SUBJECT",
    "recordStatus": "Record Incomplete",
    "deleted": False,
    "dateCreated": "2024-11-04 16:03:19",  # Use format from docs
    "dateModified": "2024-11-04 16:03:20",
    "subjectId": 326,
    "subjectOid": "OID-1",
    "subjectKey": "123-456",
    "visitId": 1,
    "parentRecordId": 34,
    "keywords": [],
    "recordData": {
        "dateCreated": "2018-10-18 06:21:46",
        "unvnum": "1",
        "dateModified": "2018-11-18 07:11:16",
        "aeser": "",
        "aeterm": "Bronchitis",
    },
}

# Corrected Metadata based on docs (no nested pagination)
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": RECORDS_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "recordId", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level GET response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_RECORD_1_DICT],  # Use single item based on pagination
}

# Mock data for POST request based on docs examples
MOCK_RECORD_POST_ITEM_1 = {
    "formKey": "REG",
    "siteName": "Minneapolis",
    "data": {"textField": "Text value"},
}
MOCK_RECORD_POST_ITEM_2 = {
    "formKey": "REG",
    "subjectKey": "651-042",
    "intervalName": "Registration",
    "data": {"textField": "Updated text"},
}

# Mock response for successful record creation (POST)
MOCK_CREATE_SUCCESS_RESPONSE_DICT = {
    "jobId": "9663fe34-eec7-460a-a820-097f1eb2875e",
    "batchId": "c3q191e4-f894-72cd-a753-b37283eh0866",
    "state": "created",
    "dateCreated": "2024-11-04 16:05:00",  # Add dateCreated
    # Add other optional fields from JobStatusModel if needed for specific tests
    "dateModified": None,
    "progress": None,
    "resultUrl": None,
    "error": None,
}


# --- Test Cases ---
@respx.mock
def test_list_records_success(records_client, client):
    """Test successful retrieval of records list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{RECORDS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = records_client.list_records(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], RecordModel)
    assert response.data[0].recordOid == "REC-1"
    assert response.data[0].formKey == "AE"
    assert isinstance(response.data[0].keywords, list)
    assert len(response.data[0].keywords) == 0
    assert isinstance(response.data[0].recordData, dict)
    assert response.data[0].recordData["aeterm"] == "Bronchitis"
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")

    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "recordId"
    assert response.pagination.sort[0].direction == "ASC"


@respx.mock
def test_list_records_with_params(records_client, client):
    """Test list_records with query parameters."""
    # Use filter syntax from docs example (==)
    expected_params = {
        "page": "1",
        "size": "10",
        "sort": "dateCreated,desc",
        "filter": "recordId==5510",  # Use == as per docs
        "recordDataFilter": "aeterm==Bronchitis",  # Use == as per docs
    }
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{RECORDS_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 1,
        "size": 10,
        "totalPages": 1,
        "totalElements": 0,
        "sort": [{"property": "dateCreated", "direction": "DESC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{RECORDS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = records_client.list_records(
        study_key=MOCK_STUDY_KEY,
        page=1,
        size=10,
        sort="dateCreated,desc",
        filter="recordId==5510",
        record_data_filter="aeterm==Bronchitis",
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "1"
    assert request.url.params["size"] == "10"
    assert request.url.params["sort"] == "dateCreated,desc"
    assert request.url.params["filter"] == "recordId==5510"
    assert request.url.params["recordDataFilter"] == "aeterm==Bronchitis"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.currentPage == 1  # Correct assertion to match requested page
    assert response.pagination.size == 10
    assert response.pagination.sort[0].property == "dateCreated"
    assert response.pagination.sort[0].direction == "DESC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_records_no_study_key(records_client):
    """Test list_records raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        records_client.list_records(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        records_client.list_records(study_key=None)  # type: ignore


@respx.mock
def test_create_records_success(records_client):
    """Test successful creation of records."""
    # POST endpoint returns JobStatusModel directly
    post_route = respx.post(f"{MOCK_BASE_URL}{RECORDS_ENDPOINT}").mock(
        return_value=Response(
            200, json=MOCK_CREATE_SUCCESS_RESPONSE_DICT
        )  # Assuming 200 OK based on JobStatus return
    )

    records_to_create = [
        RecordPostItem(**MOCK_RECORD_POST_ITEM_1),
        RecordPostItem(**MOCK_RECORD_POST_ITEM_2),
    ]

    # Assuming create_records returns JobStatusModel directly
    response = records_client.create_records(study_key=MOCK_STUDY_KEY, records=records_to_create)

    assert post_route.called
    assert response is not None
    # Assert the response is the JobStatusModel directly
    assert isinstance(response, JobStatusModel)
    assert response.jobId == "9663fe34-eec7-460a-a820-097f1eb2875e"
    assert response.batchId == "c3q191e4-f894-72cd-a753-b37283eh0866"
    assert response.state == "created"

    # Check request body
    request = post_route.calls.last.request
    request_body = request.content
    import json

    sent_data = json.loads(request_body)
    assert isinstance(sent_data, list)
    assert len(sent_data) == 2
    # Check based on MOCK_RECORD_POST_ITEM_1 and _2
    assert sent_data[0]["formKey"] == "REG"
    assert sent_data[0]["siteName"] == "Minneapolis"
    assert sent_data[0]["data"]["textField"] == "Text value"
    assert sent_data[1]["formKey"] == "REG"
    assert sent_data[1]["subjectKey"] == "651-042"
    assert sent_data[1]["intervalName"] == "Registration"
    assert sent_data[1]["data"]["textField"] == "Updated text"
    # Ensure optional fields with None value were excluded
    assert "formId" not in sent_data[0]
    assert "subjectKey" not in sent_data[0]


@respx.mock
def test_create_records_with_email_notify(records_client):
    """Test create_records sends the email notification header."""
    email = "user@domain.com"  # Use example from docs
    post_route = respx.post(f"{MOCK_BASE_URL}{RECORDS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_CREATE_SUCCESS_RESPONSE_DICT)
    )

    records_to_create = [RecordPostItem(**MOCK_RECORD_POST_ITEM_1)]

    records_client.create_records(
        study_key=MOCK_STUDY_KEY, records=records_to_create, email_notify=email
    )

    assert post_route.called
    request = post_route.calls.last.request
    assert "x-email-notify" in request.headers
    assert request.headers["x-email-notify"] == email


def test_create_records_no_study_key(records_client):
    """Test create_records raises ValueError if study_key is missing."""
    records_to_create = [RecordPostItem(**MOCK_RECORD_POST_ITEM_1)]
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        records_client.create_records(study_key="", records=records_to_create)
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        records_client.create_records(study_key=None, records=records_to_create)  # type: ignore


def test_create_records_empty_list(records_client):
    """Test create_records raises ValueError if records list is empty."""
    with pytest.raises(ValueError, match="records list cannot be empty"):
        records_client.create_records(study_key=MOCK_STUDY_KEY, records=[])
