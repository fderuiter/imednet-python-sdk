import asyncio

import pytest

import imednet.endpoints.visits as visits
from imednet.models.visits import Visit


@pytest.mark.parametrize("use_async", [False, True])
def test_list_filters_and_path(
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    context.set_default_study_key("S1")
    ep = visits.VisitsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    capture = factory(visits, [{"visitId": 1}])
    patch = patch_build_filter(visits)

    if use_async:
        result = asyncio.run(ep.async_list(status="x"))
    else:
        result = ep.list(status="x")

    assert capture["path"] == "/api/v1/edc/studies/S1/visits"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "x", "studyKey": "S1"}
    assert isinstance(result[0], Visit)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = visits.VisitsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(visits.VisitsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", 1))
        else:
            ep.get("S1", 1)
