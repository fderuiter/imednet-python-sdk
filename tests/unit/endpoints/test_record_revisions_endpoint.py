import asyncio

import pytest

import imednet.endpoints.record_revisions as record_revisions
from imednet.models.record_revisions import RecordRevision


@pytest.mark.parametrize("use_async", [False, True])
def test_list_uses_filters(
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    context.set_default_study_key("S1")
    ep = record_revisions.RecordRevisionsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    capture = factory(record_revisions, [{"recordRevisionId": 1}])
    patch = patch_build_filter(record_revisions)

    if use_async:
        result = asyncio.run(ep.async_list(status="closed"))
    else:
        result = ep.list(status="closed")

    assert capture["path"] == "/api/v1/edc/studies/S1/recordRevisions"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "closed", "studyKey": "S1"}
    assert isinstance(result[0], RecordRevision)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = record_revisions.RecordRevisionsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(record_revisions.RecordRevisionsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", 1))
        else:
            ep.get("S1", 1)
