# Tests for the Visits API client.

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata
from imednet_sdk.models.visit import VisitModel


@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(api_key="test_key", security_key="test_sec_key")


@pytest.fixture
def visits_client(client):
    """Fixture for VisitsClient."""
    return client.visits  # Assuming integration in main client later


@respx.mock
def test_list_visits_success(visits_client, client):
    """Test successful listing of visits."""
    study_key = "STUDY101"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/visits"
    mock_response_data = [
        {
            "visitKey": "VIS001",
            "visitName": "Screening",
            "visitLabel": "Screening Visit",
            "visitOrder": 1,
            "visitDescription": "Initial screening visit",
            "visitType": "Scheduled",
            "visitWindowBefore": 7,
            "visitWindowAfter": 7,
            "visitWindowUnit": "Days",
            "visitRequired": True,
            "visitForms": ["FORM001", "FORM002"],
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

    response = visits_client.list_visits(study_key=study_key)

    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], VisitModel)
    assert response.data[0].visitKey == "VIS001"
    assert response.data[0].visitName == "Screening"
    assert response.metadata.page == 1
    assert response.metadata.totalRecords == 1


@respx.mock
def test_list_visits_with_params(visits_client, client):
    """Test listing visits with query parameters."""
    study_key = "STUDY202"
    params = {"page": 2, "size": 5, "sort": "visitOrder:asc", "filter": "visitType=Unscheduled"}
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/visits"
    mock_response = {
        "metadata": {"page": 2, "size": 5, "totalRecords": 0, "totalPages": 0},
        "data": [],
    }

    route = respx.get(mock_url, params=params).mock(return_value=Response(200, json=mock_response))

    response = visits_client.list_visits(study_key=study_key, **params)

    assert route.called
    assert isinstance(response, ApiResponse)
    assert response.metadata.page == 2
    assert response.metadata.size == 5
    assert len(response.data) == 0


def test_list_visits_missing_study_key(visits_client):
    """Test listing visits with missing study_key raises ValueError."""
    with pytest.raises(ValueError, match="study_key is required."):
        visits_client.list_visits(study_key="")

    with pytest.raises(ValueError, match="study_key is required."):
        visits_client.list_visits(study_key=None)  # type: ignore
