"""Test Forms Endpoint module."""

import pytest

import imednet.endpoints.forms as forms
from imednet.errors import NotFoundError
from imednet.errors.validation import ConfigurationError
from imednet.models.forms import Form


def test_list_requires_study_key_and_page_size(
    monkeypatch, dummy_client, context, paginator_factory, patch_build_filter
):
    """Test the test list requires study key and page size functionality."""
    ep = forms.FormsEndpoint(dummy_client, context)
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
    """Test the test get success functionality."""
    ep = forms.FormsEndpoint(dummy_client, context)
    called = {}

    def fake_impl(self, client, paginator, *, study_key=None, **filters):
        """Test the fake impl functionality."""
        called["study_key"] = study_key
        called["filters"] = filters
        return [Form(form_id=1)]

    monkeypatch.setattr(forms.FormsEndpoint, "_list_sync", fake_impl)

    res = ep.get("S1", 1)

    assert called == {"study_key": "S1", "filters": {"formId": 1}}
    assert isinstance(res, Form)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test the test get not found functionality."""
    ep = forms.FormsEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, **filters):
        """Test the fake impl functionality."""
        return []

    monkeypatch.setattr(forms.FormsEndpoint, "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", 1)


def test_list_makes_request_per_call(dummy_client, context, paginator_factory):
    """Test the test list makes request per call functionality."""
    ep = forms.FormsEndpoint(dummy_client, context)
    capture = paginator_factory(forms, [{"formId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1")

    assert capture["count"] == 2


def test_list_different_study_keys_make_separate_requests(dummy_client, context, paginator_factory):
    """Test the test list different study keys make separate requests functionality."""
    ep = forms.FormsEndpoint(dummy_client, context)
    capture = paginator_factory(forms, [{"formId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S2")

    assert capture["count"] == 2
