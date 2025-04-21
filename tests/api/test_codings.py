# Tests for the Codings API client.

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata
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
    study_key = "STUDY789"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/codings"
    mock_response_data = [
        {
            "codingKey": "COD001",
            "codingName": "MedDRA",
            "codingDescription": "Medical Dictionary for Regulatory Activities",
            "codingVersion": "27.0",
            "codingType": "Adverse Event",
            "codingScope": "Study",
            "codingStatus": "Active",
            "codingDictionary": "MedDRA",
            "codingLevel": "PT",
            "codingTerm": "Headache",
            "codingCode": "10019906",
            "codingPreferredTerm": "Headache",
            "codingMeddraLevel": "PT",
            "codingMeddraVersion": "27.0",
            "codingWhoDrugCode": None,
            "codingWhoDrugName": None,
            "codingWhoDrugAtcCode": None,
            "codingWhoDrugAtcName": None,
            "codingWhoDrugVersion": None,
            "codingWhoDrugStatus": None,
            "codingWhoDrugTerm": None,
            "codingWhoDrugPreferredTerm": None,
            "codingWhoDrugMeddraCode": None,
            "codingWhoDrugMeddraName": None,
            "codingWhoDrugMeddraLevel": None,
            "codingWhoDrugMeddraVersion": None,
            "codingWhoDrugWhoArtCode": None,
            "codingWhoDrugWhoArtName": None,
            "codingWhoDrugWhoArtLevel": None,
            "codingWhoDrugWhoArtVersion": None,
            "codingWhoDrugWhoArtStatus": None,
            "codingWhoDrugWhoArtTerm": None,
            "codingWhoDrugWhoArtPreferredTerm": None,
            "codingWhoDrugWhoArtMeddraCode": None,
            "codingWhoDrugWhoArtMeddraName": None,
            "codingWhoDrugWhoArtMeddraLevel": None,
            "codingWhoDrugWhoArtMeddraVersion": None,
            "codingWhoDrugWhoArtWhoCode": None,
            "codingWhoDrugWhoArtWhoName": None,
            "codingWhoDrugWhoArtWhoLevel": None,
            "codingWhoDrugWhoArtWhoVersion": None,
            "codingWhoDrugWhoArtWhoStatus": None,
            "codingWhoDrugWhoArtWhoTerm": None,
            "codingWhoDrugWhoArtWhoPreferredTerm": None,
            "codingWhoDrugWhoArtWhoWhoMeddraCode": None,
            "codingWhoDrugWhoArtWhoWhoMeddraName": None,
            "codingWhoDrugWhoArtWhoWhoMeddraLevel": None,
            "codingWhoDrugWhoArtWhoWhoMeddraVersion": None,
            "codingWhoDrugWhoArtWhoWhoWhoCode": None,
            "codingWhoDrugWhoArtWhoWhoWhoName": None,
            "codingWhoDrugWhoArtWhoWhoWhoLevel": None,
            "codingWhoDrugWhoArtWhoWhoWhoVersion": None,
            "codingWhoDrugWhoArtWhoWhoWhoStatus": None,
            "codingWhoDrugWhoArtWhoWhoWhoTerm": None,
            "codingWhoDrugWhoArtWhoWhoWhoPreferredTerm": None,
            "codingWhoDrugWhoArtWhoWhoWhoMeddraCode": None,
            "codingWhoDrugWhoArtWhoWhoWhoMeddraName": None,
            "codingWhoDrugWhoArtWhoWhoWhoMeddraLevel": None,
            "codingWhoDrugWhoArtWhoWhoWhoMeddraVersion": None,
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

    response = codings_client.list_codings(study_key=study_key)

    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], CodingModel)
    assert response.data[0].codingKey == "COD001"
    assert response.data[0].codingName == "MedDRA"
    assert response.metadata.page == 1
    assert response.metadata.totalRecords == 1


@respx.mock
def test_list_codings_with_params(codings_client, client):
    """Test listing codings with query parameters."""
    study_key = "STUDYABC"
    params = {"page": 3, "size": 20, "sort": "codingName:desc", "filter": "codingType=AE"}
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/codings"
    mock_response = {
        "metadata": {"page": 3, "size": 20, "totalRecords": 0, "totalPages": 0},
        "data": [],
    }

    route = respx.get(mock_url, params=params).mock(return_value=Response(200, json=mock_response))

    response = codings_client.list_codings(study_key=study_key, **params)

    assert route.called
    assert isinstance(response, ApiResponse)
    assert response.metadata.page == 3
    assert response.metadata.size == 20
    assert len(response.data) == 0


def test_list_codings_missing_study_key(codings_client):
    """Test listing codings with missing study_key raises ValueError."""
    with pytest.raises(ValueError, match="study_key is required."):
        codings_client.list_codings(study_key="")

    with pytest.raises(ValueError, match="study_key is required."):
        codings_client.list_codings(study_key=None)  # type: ignore
