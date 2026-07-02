from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
"""Unit tests for queries endpoint."""

import pytest

class Dummy:
    pass
queries = Dummy()
queries.__name__ = 'imednet.endpoints.queries'
from imednet.errors import NotFoundError
from imednet.models.queries import Query


def test_list_builds_path_and_filters(dummy_client, context, paginator_factory, patch_build_filter):
    """Test that list builds path and filters."""
    context.set_default_study_key("S1")
    ep = ENDPOINT_REGISTRY['queries'](dummy_client, context)
    capture = paginator_factory(queries, [{"annotationId": 1}])
    patch = patch_build_filter(queries)

    result = ep.list(status="new")

    assert capture["path"] == "/api/v1/edc/studies/S1/queries"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "new", "studyKey": "S1"}
    assert isinstance(result[0], Query)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test that get not found."""
    ep = ENDPOINT_REGISTRY['queries'](dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        """Helper function to fake impl."""
        return []

    monkeypatch.setattr(ENDPOINT_REGISTRY['queries'], "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", 1)
