import pytest

import imednet.endpoints.forms as forms
from imednet.models.forms import Form


def test_list_requires_study_key_and_page_size(
    monkeypatch, dummy_client, context, paginator_factory, patch_build_filter
):
    ep = forms.FormsEndpoint(dummy_client, context)
    captured = paginator_factory(forms, [{"formId": 1}])
    filter_capture = patch_build_filter(forms)

    with pytest.raises(KeyError):
        ep.list()

    context.set_default_study_key("S1")
    result = ep.list(status="new")

    assert captured["path"] == "/api/v1/edc/studies/S1/forms"
    assert captured["page_size"] == 500
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "new"}
    assert isinstance(result[0], Form)


def test_get_success(dummy_client, context, paginator_factory, patch_build_filter):
    ep = forms.FormsEndpoint(dummy_client, context)
    captured = paginator_factory(forms, [{"formId": 1}])
    filter_capture = patch_build_filter(forms)

    res = ep.get("S1", 1)

    assert captured["path"] == "/api/v1/edc/studies/S1/forms"
    assert filter_capture["filters"] == {"formId": 1}
    assert isinstance(res, Form)


def test_get_not_found(dummy_client, context, paginator_factory):
    ep = forms.FormsEndpoint(dummy_client, context)
    paginator_factory(forms, [])

    with pytest.raises(ValueError):
        ep.get("S1", 1)


def test_list_caches_by_study_key(dummy_client, context, paginator_factory):
    ep = forms.FormsEndpoint(dummy_client, context)
    capture = paginator_factory(forms, [{"formId": 1}])

    first = ep.list(study_key="S1")
    second = ep.list(study_key="S1")

    assert capture["count"] == 1
    assert first == second

    ep.list(study_key="S2")

    assert capture["count"] == 2


def test_list_refresh_bypasses_cache(dummy_client, context, paginator_factory):
    ep = forms.FormsEndpoint(dummy_client, context)
    capture = paginator_factory(forms, [{"formId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1", refresh=True)

    assert capture["count"] == 2
