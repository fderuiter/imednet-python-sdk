# Tests for the Users API client.

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata
from imednet_sdk.models.user import UserModel


@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(api_key="test_key", security_key="test_sec_key")


@pytest.fixture
def users_client(client):
    """Fixture for UsersClient."""
    return client.users  # Assuming integration in main client later


@respx.mock
def test_list_users_success(users_client, client):
    """Test successful listing of active users."""
    study_key = "STUDYXYZ"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/users"
    mock_response_data = [
        {
            "userKey": "USER001",
            "userName": "jdoe",
            "userFirstName": "John",
            "userLastName": "Doe",
            "userEmail": "john.doe@example.com",
            "userStatus": "Active",
            "userRole": "Data Manager",
            "userSite": "Site A",
            "userLastLogin": "2023-10-26T10:00:00Z",
            "userCreated": "2023-01-15T09:00:00Z",
            "userModified": "2023-10-20T11:30:00Z",
        }
    ]
    mock_metadata = {
        "page": 1,
        "size": 10,
        "totalRecords": 1,
        "totalPages": 1,
    }
    mock_response = {"metadata": mock_metadata, "data": mock_response_data}

    # Note: includeInactive defaults to 'false'
    route = respx.get(mock_url, params={"includeInactive": "false"}).mock(
        return_value=Response(200, json=mock_response)
    )

    response = users_client.list_users(study_key=study_key)

    assert route.called
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], UserModel)
    assert response.data[0].userKey == "USER001"
    assert response.data[0].userName == "jdoe"
    assert response.data[0].userStatus == "Active"
    assert response.metadata.page == 1
    assert response.metadata.totalRecords == 1


@respx.mock
def test_list_users_include_inactive(users_client, client):
    """Test listing users including inactive ones."""
    study_key = "STUDYXYZ"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/users"
    mock_response_data = [
        {
            "userKey": "USER001",
            "userName": "jdoe",
            "userFirstName": "John",
            "userLastName": "Doe",
            "userEmail": "john.doe@example.com",
            "userStatus": "Active",
            "userRole": "Data Manager",
            "userSite": "Site A",
            "userLastLogin": "2023-10-26T10:00:00Z",
            "userCreated": "2023-01-15T09:00:00Z",
            "userModified": "2023-10-20T11:30:00Z",
        },
        {
            "userKey": "USER002",
            "userName": "asmith",
            "userFirstName": "Alice",
            "userLastName": "Smith",
            "userEmail": "alice.smith@example.com",
            "userStatus": "Inactive",
            "userRole": "Investigator",
            "userSite": "Site B",
            "userLastLogin": "2023-09-01T15:00:00Z",
            "userCreated": "2023-02-20T08:00:00Z",
            "userModified": "2023-08-30T16:45:00Z",
        },
    ]
    mock_metadata = {
        "page": 1,
        "size": 10,
        "totalRecords": 2,
        "totalPages": 1,
    }
    mock_response = {"metadata": mock_metadata, "data": mock_response_data}

    route = respx.get(mock_url, params={"includeInactive": "true"}).mock(
        return_value=Response(200, json=mock_response)
    )

    response = users_client.list_users(study_key=study_key, include_inactive=True)

    assert route.called
    assert isinstance(response, ApiResponse)
    assert len(response.data) == 2
    assert response.data[0].userStatus == "Active"
    assert response.data[1].userStatus == "Inactive"
    assert response.metadata.totalRecords == 2


@respx.mock
def test_list_users_with_params(users_client, client):
    """Test listing users with pagination and sorting."""
    study_key = "STUDYXYZ"
    params = {"page": 2, "size": 5, "sort": "userName:asc", "includeInactive": "false"}
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/users"
    mock_response = {
        "metadata": {"page": 2, "size": 5, "totalRecords": 0, "totalPages": 0},
        "data": [],
    }

    route = respx.get(mock_url, params=params).mock(return_value=Response(200, json=mock_response))

    # Pass include_inactive=False explicitly, although it's the default
    response = users_client.list_users(
        study_key=study_key, page=2, size=5, sort="userName:asc", include_inactive=False
    )

    assert route.called
    assert isinstance(response, ApiResponse)
    assert response.metadata.page == 2
    assert response.metadata.size == 5
    assert len(response.data) == 0


def test_list_users_missing_study_key(users_client):
    """Test listing users with missing study_key raises ValueError."""
    with pytest.raises(ValueError, match="study_key is required."):
        users_client.list_users(study_key="")

    with pytest.raises(ValueError, match="study_key is required."):
        users_client.list_users(study_key=None)  # type: ignore
