import asyncio

import pytest

import imednet.endpoints.forms as forms
from imednet.models.forms import Form


@pytest.mark.parametrize("use_async", [False, True])
def test_list_requires_study_key_and_page_size(
    monkeypatch,
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    ep = forms.FormsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    captured = factory(forms, [{"formId": 1}])
    filter_capture = patch_build_filter(forms)

    with pytest.raises(KeyError):
        if use_async:
            asyncio.run(ep.async_list())
        else:
            ep.list()

    context.set_default_study_key("S1")
    if use_async:
        result = asyncio.run(ep.async_list(status="new"))
    else:
        result = ep.list(status="new")

    assert captured["path"] == "/api/v1/edc/studies/S1/forms"
    assert captured["page_size"] == 500
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "new"}
    assert isinstance(result[0], Form)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_success(monkeypatch, dummy_client, context, use_async):
    ep = forms.FormsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    called = {}

    if use_async:

        async def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
            called["study_key"] = study_key
            called["refresh"] = refresh
            called["filters"] = filters
            return [Form(form_id=1)]

    else:

        def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
            called["study_key"] = study_key
            called["refresh"] = refresh
            called["filters"] = filters
            return [Form(form_id=1)]

    monkeypatch.setattr(forms.FormsEndpoint, "_list_impl", fake_impl)

    if use_async:
        res = asyncio.run(ep.async_get("S1", 1))
    else:
        res = ep.get("S1", 1)

    assert called == {"study_key": "S1", "refresh": True, "filters": {"formId": 1}}
    assert isinstance(res, Form)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = forms.FormsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    if use_async:

        async def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
            return []

    else:

        def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
            return []

    monkeypatch.setattr(forms.FormsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", 1))
        else:
            ep.get("S1", 1)


@pytest.mark.parametrize("use_async", [False, True])
def test_list_caches_by_study_key(
    dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = forms.FormsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    factory = paginator_factory
    capture = factory(forms, [{"formId": 1}])

    if use_async:
        first = asyncio.run(ep.async_list(study_key="S1"))
        second = asyncio.run(ep.async_list(study_key="S1"))
    else:
        first = ep.list(study_key="S1")
        second = ep.list(study_key="S1")

    assert capture["count"] == 1
    assert first == second

    if use_async:
        asyncio.run(ep.async_list(study_key="S2"))
    else:
        ep.list(study_key="S2")

    assert capture["count"] == 2


@pytest.mark.parametrize("use_async", [False, True])
def test_list_refresh_bypasses_cache(
    dummy_client, context, paginator_factory, use_async, async_paginator_factory
):
    ep = forms.FormsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        pytest.skip("Caching not supported for async endpoints")
    capture = paginator_factory(forms, [{"formId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1", refresh=True)

    assert capture["count"] == 2
