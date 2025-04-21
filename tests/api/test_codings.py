"""Tests for the Codings API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.codings import CodingsClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.models.coding import CodingModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
CODINGS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/codings"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def codings_client(client):
    """Fixture for CodingsClient."""
    return CodingsClient(client)


# --- Mock Data ---
MOCK_CODING_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "siteName": "Site A",
    "siteId": 1,
    "subjectId": 101,
    "subjectKey": "S001",
    "formId": 201,
    "formName": "Adverse Events",
    "formKey": "AE",
    "revision": 1,
    "recordId": 301,
    "variable": "AE_TERM",
    "value": "Headache",
    "codingId": 401,
    "code": "10019211",  # Example MedDRA code
    "codedBy": "coder1",
    "reason": "Standard coding",
    "dictionaryName": "MedDRA",
    "dictionaryVersion": "26.0",
    "dateCoded": "2023-06-01T10:00:00Z",
}
MOCK_CODING_2_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "siteName": "Site B",
    "siteId": 2,
    "subjectId": 102,
    "subjectKey": "S002",
    "formId": 202,
    "formName": "Concomitant Medications",
    "formKey": "CM",
    "revision": 2,
    "recordId": 302,
    "variable": "CM_NAME",
    "value": "Aspirin",
    "codingId": 402,
    "code": "10003691",  # Example WHODrug code
    "codedBy": "coder2",
    "reason": "Standard coding",
    "dictionaryName": "WHODrug",
    "dictionaryVersion": "2023-03",
    "dateCoded": "2023-06-05T11:30:00Z",
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": CODINGS_ENDPOINT,
    "timestamp": datetime.now().isoformat(),
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_CODING_1_DICT, MOCK_CODING_2_DICT],
}


# --- Test Cases ---
@respx.mock
def test_list_codings_success(codings_client):
    """Test successful retrieval of codings list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{CODINGS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = codings_client.list_codings(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, CodingModel) for item in response.data)
    assert response.data[0].codingId == 401
    assert response.data[1].codingId == 402
    assert response.data[0].dictionaryName == "MedDRA"
    assert response.data[1].dictionaryName == "WHODrug"


@respx.mock
def test_list_codings_with_params(codings_client):
    """Test list_codings with query parameters."""
    expected_params = {
        "page": "1",
        "size": "10",
        "sort": "subjectKey,asc",
        "filter": 'codedBy=="coder1"',
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{CODINGS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Mock response content doesn't matter here
    )

    codings_client.list_codings(
        study_key=MOCK_STUDY_KEY,
        page=1,
        size=10,
        sort="subjectKey,asc",
        filter='codedBy=="coder1"',
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "1"
    assert request.url.params["size"] == "10"
    assert request.url.params["sort"] == "subjectKey,asc"
    assert request.url.params["filter"] == 'codedBy=="coder1"'


def test_list_codings_no_study_key(codings_client):
    """Test list_codings raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        codings_client.list_codings(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        codings_client.list_codings(study_key=None)  # type: ignore
