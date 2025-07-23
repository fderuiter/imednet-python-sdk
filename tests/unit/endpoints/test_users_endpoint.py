import asyncio

import pytest

import imednet.endpoints.users as users
from imednet.models.users import User


@pytest.mark.parametrize("use_async", [False, True])
def test_list_requires_study_key_and_include_inactive(
    dummy_client,
    context,
    paginator_factory,
    use_async,
    async_paginator_factory,
):
    ep = users.UsersEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    capture = factory(users, [{"userId": 1}])

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_list())
        else:
            ep.list()

    if use_async:
        result = asyncio.run(ep.async_list(study_key="S1", include_inactive=True))
    else:
        result = ep.list(study_key="S1", include_inactive=True)

    assert capture["path"] == "/api/v1/edc/studies/S1/users"
    assert capture["params"] == {"includeInactive": "true"}
    assert isinstance(result[0], User)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = users.UsersEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(users.UsersEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", 1))
        else:
            ep.get("S1", 1)
