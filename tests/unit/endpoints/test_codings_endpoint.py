import asyncio

import pytest

import imednet.endpoints.codings as codings
from imednet.models.codings import Coding


@pytest.mark.parametrize("use_async", [False, True])
def test_list_requires_study_key(
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    ep = codings.CodingsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    capture = factory(codings, [{"codingId": 1}])
    patch = patch_build_filter(codings)

    with pytest.raises(KeyError):
        if use_async:
            asyncio.run(ep.async_list())
        else:
            ep.list()

    if use_async:
        result = asyncio.run(ep.async_list(study_key="S1", status="y"))
    else:
        result = ep.list(study_key="S1", status="y")

    assert capture["path"] == "/api/v1/edc/studies/S1/codings"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "y"}
    assert isinstance(result[0], Coding)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = codings.CodingsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(codings.CodingsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", "x"))
        else:
            ep.get("S1", "x")
