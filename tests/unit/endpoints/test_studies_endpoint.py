import pytest

import imednet.endpoints.studies as studies
from imednet.models.studies import Study


def test_list_builds_path_and_filters(
    monkeypatch, dummy_client, context, paginator_factory, patch_build_filter
):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])
    filter_capture = patch_build_filter(studies)

    result = ep.list(status="active")

    assert captured["path"] == "/api/v1/edc/studies"
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "active"}
    assert isinstance(result[0], Study)


def test_get_success(monkeypatch, dummy_client, context, paginator_factory, patch_build_filter):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])
    filter_capture = patch_build_filter(studies)

    res = ep.get(None, "S1")

    assert captured["path"] == "/api/v1/edc/studies"
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"studyKey": "S1"}
    assert isinstance(res, Study)


def test_get_not_found(monkeypatch, dummy_client, context, paginator_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    paginator_factory(studies, [])
    with pytest.raises(ValueError):
        ep.get(None, "missing")


def test_list_caches_results(dummy_client, context, paginator_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])

    first = ep.list()
    second = ep.list()

    assert captured["count"] == 1
    assert first == second


def test_list_refresh_bypasses_cache(dummy_client, context, paginator_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])

    ep.list()
    ep.list(refresh=True)

    assert captured["count"] == 2
