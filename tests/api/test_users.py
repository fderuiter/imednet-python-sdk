# Tests for the Users API client.

from datetime import datetime  # Import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.users import UsersClient  # Import specific client
from imednet_sdk.client import ImednetClient
# Use PaginationInfo based on _common.py
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo, SortInfo
from imednet_sdk.models.user import RoleModel, UserModel  # Add RoleModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "MOCK-STUDY"  # Use example from docs
USERS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/users"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def users_client(client):
    """Fixture for UsersClient."""
    return UsersClient(client)


# --- Mock Data ---
# Corrected mock data based on docs/reference/users.md example
MOCK_ROLE_1_DICT = {
    "dateCreated": [2024, 11, 4, 16, 3, 18, 487000000],
    "dateModified": [2024, 11, 4, 16, 3, 18, 487000000],
    "roleId": "bb5bae9d-5869-41b4-ae29-6d28f6200c85",
    "communityId": 1,
    "name": "Role name 1",
    "description": "Role description 1",
    "level": 1,
    "type": "Role type 1",
    "inactive": False,
}
MOCK_ROLE_2_DICT = {
    "dateCreated": [2024, 11, 4, 16, 3, 18, 487000000],
    "dateModified": [2024, 11, 4, 16, 3, 18, 487000000],
    "roleId": "cc6cbf0e-5869-41b4-ae29-6d28f6200c86",  # Different ID
    "communityId": 2,
    "name": "Role name 2",
    "description": "Role description 2",
    "level": 2,
    "type": "Role type 2",
    "inactive": False,
}

MOCK_USER_1_DICT = {
    "userId": "ed4cb749-9e65-40d3-a15d-cc83d4e68ded",
    "login": "wsmith1",
    "firstName": "William",
    "lastName": "Smith",
    "email": "wsmith@mednet.com",
    "userActiveInStudy": True,
    "roles": [MOCK_ROLE_1_DICT, MOCK_ROLE_2_DICT],
}
# MOCK_USER_2_DICT for inactive user if needed
MOCK_USER_2_INACTIVE_DICT = {
    "userId": "f55dc850-a076-41e4-b26e-dd94e5f79ef0",
    "login": "ajones2",
    "firstName": "Alice",
    "lastName": "Jones",
    "email": "ajones@mednet.com",
    "userActiveInStudy": False,
    "roles": [MOCK_ROLE_1_DICT],  # Example: inactive user might still have roles listed
}

# Corrected Metadata based on docs
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": USERS_ENDPOINT,
    "timestamp": "2024-11-04 16:03:18",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "login", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure for single active user
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_USER_1_DICT],  # Use single item based on pagination
}

# Mock response for including inactive users
MOCK_PAGINATION_INACTIVE_DICT = {
    "currentPage": 0,
    "size": 2,  # Adjusted for two users
    "totalPages": 1,
    "totalElements": 2,
    "sort": [{"property": "login", "direction": "ASC"}],
}
MOCK_INACTIVE_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_INACTIVE_DICT,
    "data": [MOCK_USER_2_INACTIVE_DICT, MOCK_USER_1_DICT],  # Example order
}


# --- Test Cases ---
@respx.mock
def test_list_users_success(users_client, client):
    """Test successful listing of active users."""
    # Default is includeInactive=false
    list_route = respx.get(
        f"{MOCK_BASE_URL}{USERS_ENDPOINT}", params={"includeInactive": "false"}
    ).mock(return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT))

    response = users_client.list_users(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], UserModel)
    # Assertions based on corrected mock data
    assert response.data[0].userId == "ed4cb749-9e65-40d3-a15d-cc83d4e68ded"
    assert response.data[0].login == "wsmith1"
    assert response.data[0].firstName == "William"
    assert response.data[0].lastName == "Smith"
    assert response.data[0].email == "wsmith@mednet.com"
    assert response.data[0].userActiveInStudy is True

    # Assert roles
    assert isinstance(response.data[0].roles, list)
    assert len(response.data[0].roles) == 2
    assert isinstance(response.data[0].roles[0], RoleModel)
    assert response.data[0].roles[0].roleId == "bb5bae9d-5869-41b4-ae29-6d28f6200c85"
    assert response.data[0].roles[0].name == "Role name 1"
    # Check date parsing for array format (assuming model handles this)
    # This might require a custom validator or pre-processing in the model
    # For now, check if it parses without error
    assert isinstance(response.data[0].roles[0].dateCreated, datetime)
    assert response.data[0].roles[0].dateCreated.year == 2024
    assert response.data[0].roles[0].dateCreated.month == 11
    assert response.data[0].roles[0].dateCreated.day == 4
    assert response.data[0].roles[0].dateCreated.hour == 16
    assert response.data[0].roles[0].dateCreated.minute == 3
    assert response.data[0].roles[0].dateCreated.second == 18
    assert response.data[0].roles[0].dateCreated.microsecond == 487000


@respx.mock
def test_list_users_include_inactive(users_client):
    """Test listing users including inactive ones."""
    list_route = respx.get(
        f"{MOCK_BASE_URL}{USERS_ENDPOINT}", params={"includeInactive": "true"}
    ).mock(return_value=Response(200, json=MOCK_INACTIVE_RESPONSE_DICT))

    response = users_client.list_users(study_key=MOCK_STUDY_KEY, include_inactive=True)

    assert list_route.called
    assert isinstance(response, ApiResponse)
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    # Check based on MOCK_INACTIVE_RESPONSE_DICT data order
    assert response.data[0].login == "ajones2"
    assert response.data[0].userActiveInStudy is False
    assert response.data[1].login == "wsmith1"
    assert response.data[1].userActiveInStudy is True
    assert response.pagination.totalElements == 2


@respx.mock
def test_list_users_with_params(users_client, client):
    """Test listing users with pagination and sorting."""
    # Correct sort format
    params = {"page": "2", "size": "5", "sort": "login,asc", "includeInactive": "false"}
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{USERS_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 2,
        "size": 5,
        "totalPages": 3,
        "totalElements": 12,
        "sort": [{"property": "login", "direction": "ASC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{USERS_ENDPOINT}", params=params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = users_client.list_users(
        study_key=MOCK_STUDY_KEY, page=2, size=5, sort="login,asc", include_inactive=False
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "2"
    assert request.url.params["size"] == "5"
    assert request.url.params["sort"] == "login,asc"
    assert request.url.params["includeInactive"] == "false"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.currentPage == 2
    assert response.pagination.size == 5
    assert response.pagination.sort[0].property == "login"
    assert response.pagination.sort[0].direction == "ASC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_users_missing_study_key(users_client):
    """Test listing users with missing study_key raises ValueError."""
    with pytest.raises(ValueError, match="study_key is required."):
        users_client.list_users(study_key="")

    with pytest.raises(ValueError, match="study_key is required."):
        users_client.list_users(study_key=None)  # type: ignore
