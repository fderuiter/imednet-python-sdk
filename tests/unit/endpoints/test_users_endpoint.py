import pytest

import imednet.endpoints.users as users
from imednet.models.users import User


def test_list_requires_study_key_and_include_inactive(dummy_client, context, paginator_factory):
    ep = users.UsersEndpoint(dummy_client, context)
    capture = paginator_factory(users, [{"userId": 1}])

    with pytest.raises(ValueError):
        ep.list()

    result = ep.list(study_key="S1", include_inactive=True)

    assert capture["path"] == "/api/v1/edc/studies/S1/users"
    assert capture["params"] == {"includeInactive": "true"}
    assert isinstance(result[0], User)


def test_get_not_found(dummy_client, context, paginator_factory):
    ep = users.UsersEndpoint(dummy_client, context)
    paginator_factory(users, [])

    with pytest.raises(ValueError):
        ep.get("S1", 1)
