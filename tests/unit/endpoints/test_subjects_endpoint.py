import asyncio

import pytest

import imednet.endpoints.subjects as subjects
from imednet.models.subjects import Subject


@pytest.mark.parametrize("use_async", [False, True])
def test_list_builds_path_with_default(
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    context.set_default_study_key("S1")
    ep = subjects.SubjectsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    capture = factory(subjects, [{"subjectKey": "x"}])
    patch = patch_build_filter(subjects)

    if use_async:
        result = asyncio.run(ep.async_list())
    else:
        result = ep.list()

    assert capture["path"] == "/api/v1/edc/studies/S1/subjects"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"studyKey": "S1"}
    assert isinstance(result[0], Subject)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = subjects.SubjectsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(subjects.SubjectsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", "X"))
        else:
            ep.get("S1", "X")
