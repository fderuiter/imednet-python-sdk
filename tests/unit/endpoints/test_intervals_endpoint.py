import asyncio

import pytest

import imednet.endpoints.intervals as intervals
from imednet.models.intervals import Interval


@pytest.mark.parametrize("use_async", [False, True])
def test_list_uses_default_study_and_page_size(
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    context.set_default_study_key("S1")
    ep = intervals.IntervalsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    captured = factory(intervals, [{"intervalId": 1}])
    filter_capture = patch_build_filter(intervals)

    if use_async:
        result = asyncio.run(ep.async_list(status="x"))
    else:
        result = ep.list(status="x")

    assert captured["path"] == "/api/v1/edc/studies/S1/intervals"
    assert captured["page_size"] == 500
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "x"}
    assert isinstance(result[0], Interval)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = intervals.IntervalsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(intervals.IntervalsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", 1))
        else:
            ep.get("S1", 1)


@pytest.mark.parametrize("use_async", [False, True])
def test_list_caches_by_study_key(
    dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = intervals.IntervalsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    capture = paginator_factory(intervals, [{"intervalId": 1}])

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
    ep = intervals.IntervalsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    capture = paginator_factory(intervals, [{"intervalId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1", refresh=True)

    assert capture["count"] == 2
