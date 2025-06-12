import imednet.endpoints.forms as forms
import pytest
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


def test_get_success(dummy_client, context, response_factory):
    ep = forms.FormsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": [{"formId": 1}]})

    res = ep.get("S1", 1)

    dummy_client.get.assert_called_once_with("/api/v1/edc/studies/S1/forms/1")
    assert isinstance(res, Form)


def test_get_not_found(dummy_client, context, response_factory):
    ep = forms.FormsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("S1", 1)
