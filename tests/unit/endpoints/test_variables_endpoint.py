import asyncio

import pytest

import imednet.endpoints.variables as variables
from imednet.models.variables import Variable


@pytest.mark.parametrize("use_async", [False, True])
def test_list_requires_study_key_page_size(
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    ep = variables.VariablesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    capture = paginator_factory(variables, [{"variableId": 1}])
    patch = patch_build_filter(variables)

    with pytest.raises(KeyError):
        if use_async:
            asyncio.run(ep.async_list())
        else:
            ep.list()

    if use_async:
        result = asyncio.run(ep.async_list(study_key="S1", name="x"))
    else:
        result = ep.list(study_key="S1", name="x")

    assert capture["path"] == "/api/v1/edc/studies/S1/variables"
    assert capture["page_size"] == 500
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"name": "x"}
    assert isinstance(result[0], Variable)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = variables.VariablesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(variables.VariablesEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", 1))
        else:
            ep.get("S1", 1)


@pytest.mark.parametrize("use_async", [False, True])
def test_list_caches_by_study_key(
    dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = variables.VariablesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    capture = paginator_factory(variables, [{"variableId": 1}])

    first = ep.list(study_key="S1")
    second = ep.list(study_key="S1")

    assert capture["count"] == 1
    assert first == second

    ep.list(study_key="S2")

    assert capture["count"] == 2


@pytest.mark.parametrize("use_async", [False, True])
def test_list_refresh_bypasses_cache(
    dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = variables.VariablesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    capture = paginator_factory(variables, [{"variableId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1", refresh=True)

    assert capture["count"] == 2
