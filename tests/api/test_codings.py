# Tests for the Codings API client.

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, Pagination, SortInfo
from imednet_sdk.models.coding import CodingModel


@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(api_key="test_key", security_key="test_sec_key")


@pytest.fixture
def codings_client(client):
    """Fixture for CodingsClient."""
    return client.codings  # Assuming integration in main client later


@respx.mock
def test_list_codings_success(codings_client, client):
    """Test successful listing of codings."""
    study_key = "PHARMADEMO"  # Use example from docs
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/codings"
    # Corrected mock response based on docs/reference/codings.md
    mock_response_data = [
        {
            "studyKey": "PHARMADEMO",
            "siteName": "Chicago Hope Hospital",
            "siteId": 128,
            "subjectId": 247,
            "subjectKey": "111-005",
            "formId": 1,
            "formName": "Adverse Event",
            "formKey": "AE",
            "revision": 2,
            "recordId": 1,
            "variable": "AETERM",
            "value": "Angina",
            "codingId": 1,
            "code": "Angina agranulocytic",
            "codedBy": "John Smith",
            "reason": "Typo fix",
            "dictionaryName": "MedDRA",
            "dictionaryVersion": "24.0",
            "dateCoded": "2024-11-04 16:03:19"
        }
    ]
    mock_metadata = { # Based on docs example
        "status": "OK",
        "method": "GET",
        "path": f"/api/v1/edc/studies/{study_key}/codings",
        "timestamp": "2024-11-04 16:03:19",
        "error": {}
    }
    mock_pagination = { # Based on docs example
        "currentPage": 0,
        "size": 25,
        "totalPages": 1,
        "totalElements": 1,
        "sort": [
            {
                "property": "recordId",
                "direction": "ASC"
            }
        ]
    }
    mock_response = {"metadata": mock_metadata, "pagination": mock_pagination, "data": mock_response_data}

    respx.get(mock_url).mock(return_value=Response(200, json=mock_response))

    response = codings_client.list_codings(study_key=study_key)

    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, Pagination) # Check for Pagination type
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], CodingModel)
    # Assertions based on corrected mock data and documented fields
    assert response.data[0].studyKey == "PHARMADEMO"
    assert response.data[0].siteName == "Chicago Hope Hospital"
    assert response.data[0].recordId == 1
    assert response.data[0].variable == "AETERM"
    assert response.data[0].code == "Angina agranulocytic"
    assert response.data[0].dictionaryName == "MedDRA"
    assert response.pagination.currentPage == 0
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "recordId"
    assert response.pagination.sort[0].direction == "ASC"


@respx.mock
def test_list_codings_with_params(codings_client, client):
    """Test listing codings with query parameters."""
    study_key = "STUDYABC"
    # Use documented param names and example values
    params = {"page": 0, "size": 20, "sort": "recordId,desc", "filter": "dictionaryName=MedDRA"}
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/codings"
    # Corrected mock response structure for an empty result
    mock_metadata = {
        "status": "OK", "method": "GET", "path": f"/api/v1/edc/studies/{study_key}/codings",
        "timestamp": "2024-11-04 16:04:00", "error": {}
    }
    mock_pagination = {
        "currentPage": 0, "size": 20, "totalPages": 0, "totalElements": 0,
        "sort": [{"property": "recordId", "direction": "DESC"}]
    }
    mock_response = {"metadata": mock_metadata, "pagination": mock_pagination, "data": []}

    # Adjust respx params matching to handle comma-separated sort
    expected_params = {"page": "0", "size": "20", "sort": "recordId,desc", "filter": "dictionaryName=MedDRA"}
    route = respx.get(mock_url, params=expected_params).mock(return_value=Response(200, json=mock_response))

    response = codings_client.list_codings(study_key=study_key, page=0, size=20, sort="recordId,desc", filter="dictionaryName=MedDRA")

    assert route.called
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, Pagination)
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 20
    assert response.pagination.totalElements == 0
    assert len(response.data) == 0
    assert response.pagination.sort[0].property == "recordId"
    assert response.pagination.sort[0].direction == "DESC"


def test_list_codings_missing_study_key(codings_client):
    """Test listing codings with missing study_key raises ValueError."""
    with pytest.raises(ValueError, match="study_key is required."):
        codings_client.list_codings(study_key="")

    with pytest.raises(ValueError, match="study_key is required."):
        codings_client.list_codings(study_key=None)  # type: ignore
