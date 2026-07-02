from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
"""Unit tests for record revisions endpoint."""

import pytest

class Dummy:
    pass
record_revisions = Dummy()
record_revisions.__name__ = 'imednet.endpoints.record_revisions'
from imednet.errors import NotFoundError
from imednet.models.record_revisions import RecordRevision


def test_list_uses_filters(dummy_client, context, paginator_factory, patch_build_filter):
    """Test that list uses filters."""
    context.set_default_study_key("S1")
    ep = ENDPOINT_REGISTRY['record_revisions'](dummy_client, context)
    capture = paginator_factory(record_revisions, [{"recordRevisionId": 1}])
    patch = patch_build_filter(record_revisions)

    result = ep.list(status="closed")

    assert capture["path"] == "/api/v1/edc/studies/S1/recordRevisions"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "closed", "studyKey": "S1"}
    assert isinstance(result[0], RecordRevision)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test that get not found."""
    ep = ENDPOINT_REGISTRY['record_revisions'](dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        """Helper function to fake impl."""
        return []

    monkeypatch.setattr(ENDPOINT_REGISTRY['record_revisions'], "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", 1)
