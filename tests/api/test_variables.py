"""Tests for the Variables API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.variables import VariablesClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.models.variable import VariableModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
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
MOCK_VARIABLE_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "variableId": 1001,
    "variableType": "TEXT",
    "variableName": "PATIENT_ID",
    "sequence": 1,
    "revision": 1,
    "disabled": False,
    "dateCreated": "2023-05-01T10:00:00Z",
    "dateModified": "2023-05-01T11:00:00Z",
    "formId": 201,
    "variableOid": "VAR_PAT_ID",
    "deleted": False,
    "formKey": "DEMOGRAPHICS",
    "formName": "Demographics Form",
    "label": "Patient ID",
    "blinded": False,
}
MOCK_VARIABLE_2_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "variableId": 1002,
    "variableType": "RADIO",
    "variableName": "SEX",
    "sequence": 2,
    "revision": 2,
    "disabled": False,
    "dateCreated": "2023-05-02T09:00:00Z",
    "dateModified": "2023-05-03T14:30:00Z",
    "formId": 201,
    "variableOid": "VAR_SEX",
    "deleted": False,
    "formKey": "DEMOGRAPHICS",
    "formName": "Demographics Form",
    "label": "Sex",
    "blinded": True,
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": VARIABLES_ENDPOINT,
    "timestamp": datetime.now().isoformat(),
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_VARIABLE_1_DICT, MOCK_VARIABLE_2_DICT],
}


# --- Test Cases ---
@respx.mock
def test_list_variables_success(variables_client):
    """Test successful retrieval of variables list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{VARIABLES_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = variables_client.list_variables(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, VariableModel) for item in response.data)
    assert response.data[0].variableName == "PATIENT_ID"
    assert response.data[1].variableName == "SEX"
    assert response.data[1].blinded is True


@respx.mock
def test_list_variables_with_params(variables_client):
    """Test list_variables with query parameters."""
    expected_params = {
        "page": "3",
        "size": "20",
        "sort": "sequence,asc",
        "filter": 'variableType=="TEXT"',
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{VARIABLES_ENDPOINT}", params=expected_params).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Mock response content doesn't matter here
    )

    variables_client.list_variables(
        study_key=MOCK_STUDY_KEY,
        page=3,
        size=20,
        sort="sequence,asc",
        filter='variableType=="TEXT"',
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "3"
    assert request.url.params["size"] == "20"
    assert request.url.params["sort"] == "sequence,asc"
    assert request.url.params["filter"] == 'variableType=="TEXT"'


def test_list_variables_no_study_key(variables_client):
    """Test list_variables raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        variables_client.list_variables(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        variables_client.list_variables(study_key=None)  # type: ignore
