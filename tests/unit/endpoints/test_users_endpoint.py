"""Test Users Endpoint module."""

import pytest

import imednet.endpoints.users as users
from imednet.errors import NotFoundError
from imednet.errors.validation import ConfigurationError
from imednet.models.users import User


def test_list_requires_study_key_and_include_inactive(dummy_client, context, paginator_factory):
    """Test the test list requires study key and include inactive functionality."""
    ep = users.UsersEndpoint(dummy_client, context)
    capture = paginator_factory(users, [{"userId": 1}])

    with pytest.raises(ConfigurationError):
        ep.list()

    result = ep.list(study_key="S1", include_inactive=True)

    assert capture["path"] == "/api/v1/edc/studies/S1/users"
    assert capture["params"] == {"includeInactive": "true"}
    assert isinstance(result[0], User)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test the test get not found functionality."""
    ep = users.UsersEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        """Test the fake impl functionality."""
        return []

    monkeypatch.setattr(users.UsersEndpoint, "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", 1)
