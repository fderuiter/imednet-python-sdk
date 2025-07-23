import asyncio

import pytest

import imednet.endpoints.studies as studies
from imednet.models.studies import Study


@pytest.mark.parametrize("use_async", [False, True])
def test_list_builds_path_and_filters(
    monkeypatch,
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    ep = studies.StudiesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    captured = factory(studies, [{"studyKey": "S1"}])
    filter_capture = patch_build_filter(studies)

    if use_async:
        result = asyncio.run(ep.async_list(status="active"))
    else:
        result = ep.list(status="active")

    assert captured["path"] == "/api/v1/edc/studies"
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "active"}
    assert isinstance(result[0], Study)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_success(
    monkeypatch,
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    ep = studies.StudiesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    captured = factory(studies, [{"studyKey": "S1"}])
    filter_capture = patch_build_filter(studies)

    if use_async:
        res = asyncio.run(ep.async_get(None, "S1"))
    else:
        res = ep.get(None, "S1")

    assert captured["path"] == "/api/v1/edc/studies"
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"studyKey": "S1"}
    assert isinstance(res, Study)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(
    monkeypatch, dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = studies.StudiesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    factory(studies, [])
    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get(None, "missing"))
        else:
            ep.get(None, "missing")


@pytest.mark.parametrize("use_async", [False, True])
def test_list_caches_results(
    dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = studies.StudiesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    captured = paginator_factory(studies, [{"studyKey": "S1"}])

    first = ep.list()
    second = ep.list()

    assert captured["count"] == 1
    assert first == second


@pytest.mark.parametrize("use_async", [False, True])
def test_list_refresh_bypasses_cache(
    dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = studies.StudiesEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    captured = paginator_factory(studies, [{"studyKey": "S1"}])

    ep.list()
    ep.list(refresh=True)

    assert captured["count"] == 2
