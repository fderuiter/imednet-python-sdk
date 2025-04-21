# Tests for the Variables API client.

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata
from imednet_sdk.models.variable import VariableModel


@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(api_key="test_key", security_key="test_sec_key")


@pytest.fixture
def variables_client(client):
    """Fixture for VariablesClient."""
    return client.variables  # Assuming integration in main client later


@respx.mock
def test_list_variables_success(variables_client, client):
    """Test successful listing of variables."""
    study_key = "STUDY123"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/variables"
    mock_response_data = [
        {
            "variableKey": "VAR001",
            "variableName": "Age",
            "variableLabel": "Patient Age",
            "variableType": "Numeric",
            "variableFormat": "##",
            "variableLength": 3,
            "variableDecimals": 0,
            "variableUnit": "years",
            "variableRequired": True,
            "variableMinValue": "0",
            "variableMaxValue": "120",
            "variableDescription": "Age of the patient in years",
            "variableCodingDictionary": None,
            "variableCodingType": None,
            "variableCodingLevel": None,
            "variableCodingVersion": None,
            "variableCodingScope": None,
            "variableCodingStatus": None,
            "variableCodingTerm": None,
            "variableCodingCode": None,
            "variableCodingPreferredTerm": None,
            "variableCodingMeddraLevel": None,
            "variableCodingMeddraVersion": None,
            "variableCodingWhoDrugCode": None,
            "variableCodingWhoDrugName": None,
            "variableCodingWhoDrugAtcCode": None,
            "variableCodingWhoDrugAtcName": None,
            "variableCodingWhoDrugVersion": None,
            "variableCodingWhoDrugStatus": None,
            "variableCodingWhoDrugTerm": None,
            "variableCodingWhoDrugPreferredTerm": None,
            "variableCodingWhoDrugMeddraCode": None,
            "variableCodingWhoDrugMeddraName": None,
            "variableCodingWhoDrugMeddraLevel": None,
            "variableCodingWhoDrugMeddraVersion": None,
            "variableCodingWhoDrugWhoArtCode": None,
            "variableCodingWhoDrugWhoArtName": None,
            "variableCodingWhoDrugWhoArtLevel": None,
            "variableCodingWhoDrugWhoArtVersion": None,
            "variableCodingWhoDrugWhoArtStatus": None,
            "variableCodingWhoDrugWhoArtTerm": None,
            "variableCodingWhoDrugWhoArtPreferredTerm": None,
            "variableCodingWhoDrugWhoArtMeddraCode": None,
            "variableCodingWhoDrugWhoArtMeddraName": None,
            "variableCodingWhoDrugWhoArtMeddraLevel": None,
            "variableCodingWhoDrugWhoArtMeddraVersion": None,
            "variableCodingWhoDrugWhoArtWhoCode": None,
            "variableCodingWhoDrugWhoArtWhoName": None,
            "variableCodingWhoDrugWhoArtWhoLevel": None,
            "variableCodingWhoDrugWhoArtWhoVersion": None,
            "variableCodingWhoDrugWhoArtWhoStatus": None,
            "variableCodingWhoDrugWhoArtWhoTerm": None,
            "variableCodingWhoDrugWhoArtWhoPreferredTerm": None,
            "variableCodingWhoDrugWhoArtWhoMeddraCode": None,
            "variableCodingWhoDrugWhoArtWhoMeddraName": None,
            "variableCodingWhoDrugWhoArtWhoMeddraLevel": None,
            "variableCodingWhoDrugWhoArtWhoMeddraVersion": None,
            "variableCodingWhoDrugWhoArtWhoWhoCode": None,
            "variableCodingWhoDrugWhoArtWhoWhoName": None,
            "variableCodingWhoDrugWhoArtWhoWhoLevel": None,
            "variableCodingWhoDrugWhoArtWhoWhoVersion": None,
            "variableCodingWhoDrugWhoArtWhoWhoStatus": None,
            "variableCodingWhoDrugWhoArtWhoWhoTerm": None,
            "variableCodingWhoDrugWhoArtWhoWhoPreferredTerm": None,
            "variableCodingWhoDrugWhoArtWhoWhoMeddraCode": None,
            "variableCodingWhoDrugWhoArtWhoWhoMeddraName": None,
            "variableCodingWhoDrugWhoArtWhoWhoMeddraLevel": None,
            "variableCodingWhoDrugWhoArtWhoWhoMeddraVersion": None,
        }
    ]
    mock_metadata = {
        "page": 1,
        "size": 10,
        "totalRecords": 1,
        "totalPages": 1,
    }
    mock_response = {"metadata": mock_metadata, "data": mock_response_data}

    respx.get(mock_url).mock(return_value=Response(200, json=mock_response))

    response = variables_client.list_variables(study_key=study_key)

    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], VariableModel)
    assert response.data[0].variableKey == "VAR001"
    assert response.data[0].variableName == "Age"
    assert response.metadata.page == 1
    assert response.metadata.totalRecords == 1


@respx.mock
def test_list_variables_with_params(variables_client, client):
    """Test listing variables with query parameters."""
    study_key = "STUDY456"
    params = {"page": 2, "size": 5, "sort": "variableName:asc", "filter": "variableType=Numeric"}
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/variables"
    mock_response = {
        "metadata": {"page": 2, "size": 5, "totalRecords": 0, "totalPages": 0},
        "data": [],
    }

    route = respx.get(mock_url, params=params).mock(return_value=Response(200, json=mock_response))

    response = variables_client.list_variables(study_key=study_key, **params)

    assert route.called
    assert isinstance(response, ApiResponse)
    assert response.metadata.page == 2
    assert response.metadata.size == 5
    assert len(response.data) == 0


def test_list_variables_missing_study_key(variables_client):
    """Test listing variables with missing study_key raises ValueError."""
    with pytest.raises(ValueError, match="study_key is required."):
        variables_client.list_variables(study_key="")

    with pytest.raises(ValueError, match="study_key is required."):
        variables_client.list_variables(study_key=None)  # type: ignore
