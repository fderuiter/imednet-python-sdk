# Tests for the Variables API client.

from datetime import datetime # Import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.variables import VariablesClient # Import specific client
from imednet_sdk.client import ImednetClient
# Use Pagination and SortInfo based on documentation structure
from imednet_sdk.models._common import ApiResponse, Metadata, Pagination, SortInfo
from imednet_sdk.models.variable import VariableModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "PHARMADEMO" # Use example from docs
VARIABLES_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/variables"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def variables_client(client):
    """Fixture for VariablesClient."""
    return VariablesClient(client)


# --- Mock Data ---
# Corrected mock data based on docs/reference/variables.md example
MOCK_VARIABLE_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "variableId": 1,
    "variableType": "RADIO",
    "variableName": "Pain Level",
    "sequence": 1,
    "revision": 1,
    "disabled": False,
    "dateCreated": "2024-11-04 16:03:19", # Use format from docs
    "dateModified": "2024-11-04 16:03:20",
    "formId": 108727,
    "variableOid": "OID-1",
    "deleted": False,
    "formKey": "FORM_1",
    "formName": "Pre-procedure screening",
    "label": "Select patient pain level between 1 and 10",
    "blinded": False
}
# MOCK_VARIABLE_2_DICT can be added if needed

# Corrected Metadata based on docs
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET", # Added method
    "path": VARIABLES_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19", # Use fixed timestamp
    "error": {}
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1, # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [
        {
            "property": "variableId", # Use 'property'
            "direction": "ASC"
        }
    ]
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_VARIABLE_1_DICT], # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_variables_success(variables_client):
    """Test successful listing of variables."""
    list_route = respx.get(f"{MOCK_BASE_URL}{VARIABLES_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = variables_client.list_variables(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    # Assert pagination is present and correct type
    assert isinstance(response.pagination, Pagination)
    assert response.metadata.status == "OK"
    assert response.metadata.path == VARIABLES_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "variableId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], VariableModel)
    # Assertions based on corrected mock data
    assert response.data[0].variableId == 1
    assert response.data[0].variableName == "Pain Level"
    assert response.data[0].variableType == "RADIO"
    assert response.data[0].formKey == "FORM_1"
    assert response.data[0].formName == "Pre-procedure screening"
    assert response.data[0].label == "Select patient pain level between 1 and 10"
    assert response.data[0].disabled is False
    assert response.data[0].deleted is False
    assert response.data[0].blinded is False
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")
    assert response.data[0].dateModified == datetime.fromisoformat("2024-11-04 16:03:20")


@respx.mock
def test_list_variables_with_params(variables_client):
    """Test listing variables with query parameters."""
    # Correct sort and filter syntax
    params = {"page": "2", "size": "5", "sort": "variableName,asc", "filter": "variableType==RADIO"}
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{VARIABLES_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 2, "size": 5, "totalPages": 4, "totalElements": 18,
        "sort": [{"property": "variableName", "direction": "ASC"}]
    }
    mock_response = {"metadata": mock_metadata, "pagination": mock_pagination, "data": []} # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{VARIABLES_ENDPOINT}", params=params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = variables_client.list_variables(
        study_key=MOCK_STUDY_KEY, page=2, size=5, sort="variableName,asc", filter="variableType==RADIO"
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "2"
    assert request.url.params["size"] == "5"
    assert request.url.params["sort"] == "variableName,asc"
    assert request.url.params["filter"] == "variableType==RADIO"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, Pagination)
    assert response.pagination.currentPage == 2
    assert response.pagination.size == 5
    assert response.pagination.sort[0].property == "variableName"
    assert response.pagination.sort[0].direction == "ASC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0 # Based on mock response


def test_list_variables_missing_study_key(variables_client):
    """Test listing variables with missing study_key raises ValueError."""
    # Match error message from client implementation
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        variables_client.list_variables(study_key="")

    with pytest.raises(ValueError, match="study_key cannot be empty"):
        variables_client.list_variables(study_key=None)  # type: ignore
