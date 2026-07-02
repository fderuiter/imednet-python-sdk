from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
"""Unit tests for forms endpoint."""

import pytest

class Dummy:
    pass
forms = Dummy()
forms.__name__ = 'imednet.endpoints.forms'
from imednet.errors import NotFoundError
from imednet.errors.validation import ConfigurationError
from imednet.models.forms import Form


def test_list_requires_study_key_and_page_size(
    monkeypatch, dummy_client, context, paginator_factory, patch_build_filter
):
    """Test that list requires study key and page size."""
    ep = ENDPOINT_REGISTRY['forms'](dummy_client, context)
    captured = paginator_factory(forms, [{"formId": 1}])
    filter_capture = patch_build_filter(forms)

    with pytest.raises(ConfigurationError):
        ep.list()

    context.set_default_study_key("S1")
    result = ep.list(status="new")

    assert captured["path"] == "/api/v1/edc/studies/S1/forms"
    assert captured["page_size"] == 500
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "new"}
    assert isinstance(result[0], Form)


def test_get_success(monkeypatch, dummy_client, context):
    """Test that get success."""
    ep = ENDPOINT_REGISTRY['forms'](dummy_client, context)
    called = {}

    def fake_impl(self, client, paginator, *, study_key=None, **filters):
        """Helper function to fake impl."""
        called["study_key"] = study_key
        called["filters"] = filters
        return [Form(form_id=1)]

    monkeypatch.setattr(ENDPOINT_REGISTRY['forms'], "_list_sync", fake_impl)

    res = ep.get("S1", 1)

    assert called == {"study_key": "S1", "filters": {"formId": 1}}
    assert isinstance(res, Form)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test that get not found."""
    ep = ENDPOINT_REGISTRY['forms'](dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, **filters):
        """Helper function to fake impl."""
        return []

    monkeypatch.setattr(ENDPOINT_REGISTRY['forms'], "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", 1)


def test_list_makes_request_per_call(dummy_client, context, paginator_factory):
    """Test that list makes request per call."""
    ep = ENDPOINT_REGISTRY['forms'](dummy_client, context)
    capture = paginator_factory(forms, [{"formId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1")

    assert capture["count"] == 2


def test_list_different_study_keys_make_separate_requests(dummy_client, context, paginator_factory):
    """Test that list different study keys make separate requests."""
    ep = ENDPOINT_REGISTRY['forms'](dummy_client, context)
    capture = paginator_factory(forms, [{"formId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S2")

    assert capture["count"] == 2
