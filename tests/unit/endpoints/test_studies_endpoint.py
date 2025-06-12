import pytest
from unittest.mock import MagicMock

import imednet.endpoints.studies as studies
from imednet.models.studies import Study


def test_list_builds_path_and_filters(monkeypatch, dummy_client, context, paginator_factory, patch_build_filter):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])
    filter_capture = patch_build_filter(studies)

    result = ep.list(status="active")

    assert captured["path"] == "/api/v1/edc/studies"
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "active"}
    assert isinstance(result[0], Study)


def test_get_success(dummy_client, context, response_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": [{"studyKey": "S1"}]})

    res = ep.get("S1")

    dummy_client.get.assert_called_once_with("/api/v1/edc/studies/S1")
    assert isinstance(res, Study)


def test_get_not_found(dummy_client, context, response_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("missing")
