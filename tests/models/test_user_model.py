"""Tests for user-related data models."""

from datetime import datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from imednet_sdk.models import ApiResponse, UserModel, UserRole
from imednet_sdk.models._common import Metadata, PaginationInfo, SortInfo


def test_user_role_creation():
    """Test creating a UserRole with valid data."""
    role_data = {
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
    role = UserRole(**role_data)
    assert role.roleId == "bb5bae9d-5869-41b4-ae29-6d28f6200c85"
    assert role.name == "Role name 1"
    assert not role.inactive


def test_user_role_date_array_conversion():
    """Test conversion of date arrays to datetime objects."""
    date_array = [2024, 11, 4, 16, 3, 18, 487000000]
    dt = UserRole.from_date_array(date_array)
    assert isinstance(dt, datetime)
    assert dt.year == 2024
    assert dt.month == 11
    assert dt.microsecond == 487000


def test_user_creation():
    """Test creating a UserModel with valid data."""
    user_data = {
        "userId": "ed4cb749-9e65-40d3-a15d-cc83d4e68ded",
        "login": "wsmith1",
        "firstName": "William",
        "lastName": "Smith",
        "email": "wsmith@mednet.com",
        "userActiveInStudy": True,
        "roles": [
            {
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
        ],
    }
    user = UserModel(**user_data)
    assert user.userId == "ed4cb749-9e65-40d3-a15d-cc83d4e68ded"
    assert user.login == "wsmith1"
    assert len(user.roles) == 1
    assert user.roles[0].name == "Role name 1"


def test_user_missing_required_field():
    """Test validation error when required field is missing."""
    user_data = {
        "userId": "ed4cb749-9e65-40d3-a15d-cc83d4e68ded",
        # Missing login field
        "firstName": "William",
        "lastName": "Smith",
        "email": "wsmith@mednet.com",
        "userActiveInStudy": True,
        "roles": [],
    }
    with pytest.raises(ValidationError):
        UserModel(**user_data)


def test_user_list_validation():
    """Test validating a list of users using TypeAdapter."""
    users_data = [
        {
            "userId": "ed4cb749-9e65-40d3-a15d-cc83d4e68ded",
            "login": "wsmith1",
            "firstName": "William",
            "lastName": "Smith",
            "email": "wsmith@mednet.com",
            "userActiveInStudy": True,
            "roles": [],
        }
    ]
    adapter = TypeAdapter(list[UserModel])
    users = adapter.validate_python(users_data)
    assert len(users) == 1
    assert users[0].login == "wsmith1"


def test_api_response_with_users():
    """Test API response containing users."""
    response_data = {
        "metadata": {
            "status": "OK",
            "method": "GET",
            "path": "/api/v1/edc/studies/MOCK-STUDY/users",
            "timestamp": "2024-11-04 16:03:18",
            "error": {},
        },
        "pagination": {
            "currentPage": 0,
            "size": 25,
            "totalPages": 1,
            "totalElements": 1,
            "sort": [{"property": "login", "direction": "ASC"}],
        },
        "data": [
            {
                "userId": "ed4cb749-9e65-40d3-a15d-cc83d4e68ded",
                "login": "wsmith1",
                "firstName": "William",
                "lastName": "Smith",
                "email": "wsmith@mednet.com",
                "userActiveInStudy": True,
                "roles": [],
            }
        ],
    }
    response = ApiResponse[list[UserModel]].model_validate(response_data)
    assert response.metadata.status == "OK"
    assert len(response.data) == 1
    assert response.data[0].login == "wsmith1"
