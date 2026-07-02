from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
"""Unit tests for codings endpoint."""

import pytest

class Dummy:
    pass
codings = Dummy()
codings.__name__ = 'imednet.endpoints.codings'
from imednet.errors import NotFoundError
from imednet.errors.validation import ConfigurationError
from imednet.models.codings import Coding


def test_list_requires_study_key(dummy_client, context, paginator_factory, patch_build_filter):
    """Test that list requires study key."""
    ep = ENDPOINT_REGISTRY['codings'](dummy_client, context)
    capture = paginator_factory(codings, [{"codingId": 1}])
    patch = patch_build_filter(codings)

    with pytest.raises(ConfigurationError):
        ep.list()

    result = ep.list(study_key="S1", status="y")

    assert capture["path"] == "/api/v1/edc/studies/S1/codings"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "y"}
    assert isinstance(result[0], Coding)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test that get not found."""
    ep = ENDPOINT_REGISTRY['codings'](dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        """Helper function to fake impl."""
        return []

    monkeypatch.setattr(ENDPOINT_REGISTRY['codings'], "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", "x")
