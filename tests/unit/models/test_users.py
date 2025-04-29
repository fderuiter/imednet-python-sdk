from datetime import datetime

from imednet.models.users import Role, User


def test_role_initialization():
    role = Role(
        dateCreated="2023-01-01T00:00:00",
        dateModified="2023-01-02T00:00:00",
        roleId="123",
        communityId=1,
        name="Test Role",
        description="Test Description",
        level=2,
        type="admin",
        inactive=False,
    )
    assert isinstance(role.date_created, datetime)
    assert isinstance(role.date_modified, datetime)
    assert role.role_id == "123"
    assert role.community_id == 1
    assert role.name == "Test Role"
    assert role.description == "Test Description"
    assert role.level == 2
    assert role.type == "admin"
    assert role.inactive is False


def test_role_default_values():
    role = Role()
    assert isinstance(role.date_created, datetime)
    assert isinstance(role.date_modified, datetime)
    assert role.role_id == ""
    assert role.community_id == 0
    assert role.name == ""
    assert role.description == ""
    assert role.level == 0
    assert role.type == ""
    assert role.inactive is False


def test_user_initialization():
    user = User(
        userId="user123",
        login="testuser",
        firstName="John",
        lastName="Doe",
        email="john@example.com",
        userActiveInStudy=True,
        roles=[Role(name="Test Role")],
    )
    assert user.user_id == "user123"
    assert user.login == "testuser"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert user.user_active_in_study is True
    assert len(user.roles) == 1
    assert user.roles[0].name == "Test Role"


def test_user_name_property():
    user = User(firstName="John", lastName="Doe")
    assert user.name == "John Doe"

    user = User(firstName="John", lastName="")
    assert user.name == "John"

    user = User(firstName="", lastName="Doe")
    assert user.name == "Doe"

    user = User(firstName="", lastName="")
    assert user.name == ""


def test_from_json_methods():
    role_data = {"dateCreated": "2023-01-01T00:00:00", "roleId": "123", "name": "Test Role"}
    role = Role.from_json(role_data)
    assert role.role_id == "123"
    assert role.name == "Test Role"

    user_data = {"userId": "user123", "firstName": "John", "lastName": "Doe", "roles": [role_data]}
    user = User.from_json(user_data)
    assert user.user_id == "user123"
    assert user.name == "John Doe"
    assert len(user.roles) == 1
