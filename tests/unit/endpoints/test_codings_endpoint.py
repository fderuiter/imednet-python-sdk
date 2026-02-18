import pytest

import imednet.endpoints.codings as codings
from imednet.models.codings import Coding


def test_list_requires_study_key(dummy_client, context, paginator_factory, patch_build_filter):
    ep = codings.CodingsEndpoint(dummy_client, context)
    capture = paginator_factory(codings, [{"codingId": 1}])
    patch = patch_build_filter(codings)

    with pytest.raises(KeyError):
        ep.list()

    result = ep.list(study_key="S1", status="y")

    assert capture["path"] == "/api/v1/edc/studies/S1/codings"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "y"}
    assert isinstance(result[0], Coding)


def test_get_not_found(monkeypatch, dummy_client, context):
    ep = codings.CodingsEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(codings.CodingsEndpoint, "_list_sync", fake_impl)

    with pytest.raises(ValueError):
        ep.get("S1", "x")
