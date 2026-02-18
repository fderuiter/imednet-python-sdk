import pytest

import imednet.endpoints.record_revisions as record_revisions
from imednet.models.record_revisions import RecordRevision


def test_list_uses_filters(dummy_client, context, paginator_factory, patch_build_filter):
    context.set_default_study_key("S1")
    ep = record_revisions.RecordRevisionsEndpoint(dummy_client, context)
    capture = paginator_factory(record_revisions, [{"recordRevisionId": 1}])
    patch = patch_build_filter(record_revisions)

    result = ep.list(status="closed")

    assert capture["path"] == "/api/v1/edc/studies/S1/recordRevisions"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "closed", "studyKey": "S1"}
    assert isinstance(result[0], RecordRevision)


def test_get_not_found(monkeypatch, dummy_client, context):
    ep = record_revisions.RecordRevisionsEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(record_revisions.RecordRevisionsEndpoint, "_list_sync", fake_impl)

    with pytest.raises(ValueError):
        ep.get("S1", 1)
