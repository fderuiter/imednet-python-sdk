"""Tests for user-related data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet_sdk.api.users import UserModel, UserRole

# Sample valid data based on docs/reference/users.md
VALID_USER_ROLE_DATA = {
    "dateCreated": [2024, 11, 4, 16, 3, 18, 487000000],
    "dateModified": [2024, 11, 4, 16, 3, 18, 487000000],
    "roleId": "bb5bae9d-5869-41b4-ae29-6d28f6200c85",
    "communityId": 1,
    "name": "Role name 1",
    "description": "Role description 1",
    "level": 1,
    "type": "Role type 1",
    "inactive": False,  # Explicitly setting default
}

VALID_USER_DATA = {
    "userId": "ed4cb749-9e65-40d3-a15d-cc83d4e68ded",
    "login": "wsmith1",
    "firstName": "William",
    "lastName": "Smith",
    "email": "wsmith@mednet.com",
    "userActiveInStudy": True,
    "roles": [VALID_USER_ROLE_DATA],
}

# --- UserRole Tests ---


def test_user_role_validation():
    """Test successful validation of UserRole."""
    model = UserRole.model_validate(VALID_USER_ROLE_DATA)

    # Access the @property which returns datetime
    created_dt = model.created_datetime  # Use renamed property
    modified_dt = model.modified_datetime  # Use renamed property

    # Check properties that convert date arrays
    assert isinstance(created_dt, datetime)
    assert created_dt == datetime(2024, 11, 4, 16, 3, 18, 487000)
    assert isinstance(modified_dt, datetime)
    assert modified_dt == datetime(2024, 11, 4, 16, 3, 18, 487000)

    # Check other fields
    assert model.roleId == VALID_USER_ROLE_DATA["roleId"]
    assert model.communityId == VALID_USER_ROLE_DATA["communityId"]
    assert model.name == VALID_USER_ROLE_DATA["name"]
    assert model.description == VALID_USER_ROLE_DATA["description"]
    assert model.level == VALID_USER_ROLE_DATA["level"]
    assert model.type == VALID_USER_ROLE_DATA["type"]
    assert model.inactive == VALID_USER_ROLE_DATA["inactive"]


def test_user_role_defaults():
    """Test default values for boolean fields when not provided."""
    minimal_data = VALID_USER_ROLE_DATA.copy()
    del minimal_data["inactive"]
    model = UserRole.model_validate(minimal_data)
    assert model.inactive is False


def test_user_role_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_USER_ROLE_DATA.copy()
    del invalid_data["roleId"]
    with pytest.raises(ValidationError) as excinfo:
        UserRole.model_validate(invalid_data)
    assert "roleId" in str(excinfo.value)


def test_user_role_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_USER_ROLE_DATA.copy()
    invalid_data["communityId"] = "not-an-int"
    with pytest.raises(ValidationError) as excinfo:
        UserRole.model_validate(invalid_data)
    assert "communityId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_date = VALID_USER_ROLE_DATA.copy()
    invalid_data_date["dateCreated"] = [2024, 11]  # Invalid array length/format
    # Pydantic will raise ValidationError due to the field_validator
    with pytest.raises(ValidationError) as excinfo_date:
        UserRole.model_validate(invalid_data_date)
    # Check that the error relates to the dateCreated field and the validator message
    assert "dateCreated" in str(excinfo_date.value)
    assert "Date array must be a list with at least 6 integer elements" in str(excinfo_date.value)


def test_user_role_serialization():
    """Test serialization of the UserRole model."""
    model = UserRole.model_validate(VALID_USER_ROLE_DATA)
    # Use by_alias=True because dateCreated/Modified use aliases
    dump = model.model_dump(by_alias=True)

    # Serialization should dump the original array (from _dateCreated/_dateModified via alias),
    # not the datetime property
    expected_data = VALID_USER_ROLE_DATA.copy()
    assert dump == expected_data


# --- UserModel Tests ---


def test_user_model_validation():
    """Test successful validation of UserModel with valid data."""
    model = UserModel.model_validate(VALID_USER_DATA)

    assert model.userId == VALID_USER_DATA["userId"]
    assert model.login == VALID_USER_DATA["login"]
    assert model.firstName == VALID_USER_DATA["firstName"]
    assert model.lastName == VALID_USER_DATA["lastName"]
    assert model.email == VALID_USER_DATA["email"]
    assert model.userActiveInStudy == VALID_USER_DATA["userActiveInStudy"]

    assert isinstance(model.roles, list)
    assert len(model.roles) == 1
    assert isinstance(model.roles[0], UserRole)
    assert model.roles[0].roleId == VALID_USER_ROLE_DATA["roleId"]


def test_user_model_empty_roles():
    """Test validation with an empty roles list."""
    data_empty_roles = VALID_USER_DATA.copy()
    data_empty_roles["roles"] = []
    model = UserModel.model_validate(data_empty_roles)
    assert model.roles == []


def test_user_model_missing_roles():
    """Test validation when the optional roles field is missing."""
    data_missing_roles = VALID_USER_DATA.copy()
    del data_missing_roles["roles"]
    model = UserModel.model_validate(data_missing_roles)
    assert model.roles == []  # Should default to empty list


def test_user_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_USER_DATA.copy()
    del invalid_data["login"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        UserModel.model_validate(invalid_data)

    assert "login" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_user_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_USER_DATA.copy()
    invalid_data["userActiveInStudy"] = "maybe"

    with pytest.raises(ValidationError) as excinfo:
        UserModel.model_validate(invalid_data)

    assert "userActiveInStudy" in str(excinfo.value)
    assert "Input should be a valid boolean" in str(excinfo.value)

    invalid_data_list = VALID_USER_DATA.copy()
    invalid_data_list["roles"] = "not-a-list"
    with pytest.raises(ValidationError) as excinfo_list:
        UserModel.model_validate(invalid_data_list)
    assert "roles" in str(excinfo_list.value)
    assert "list" in str(excinfo_list.value).lower()

    invalid_data_list_item = VALID_USER_DATA.copy()
    invalid_data_list_item["roles"] = [{"roleId": 123}]  # Invalid item type
    with pytest.raises(ValidationError) as excinfo_item:
        UserModel.model_validate(invalid_data_list_item)
    error_str = str(excinfo_item.value)
    assert "roles.0" in error_str
    assert "roles.0.roleId" in error_str or "roles.0.dateCreated" in error_str


def test_user_model_serialization():
    """Test serialization of the UserModel."""
    model = UserModel.model_validate(VALID_USER_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_USER_DATA.copy()
    # Adjust nested model serialization if needed
    role_model = UserRole.model_validate(VALID_USER_ROLE_DATA)
    expected_role_dump = role_model.model_dump(by_alias=True)

    # Check basic fields match
    for key, value in expected_data.items():
        if key != "roles":
            assert dump[key] == value

    # Check nested UserRole serialization
    assert isinstance(dump["roles"], list)
    assert len(dump["roles"]) == 1
    # The dump of the nested role should match the expected dump based on aliases
    assert dump["roles"][0] == expected_role_dump


# Add more tests for edge cases, multiple roles, etc.
