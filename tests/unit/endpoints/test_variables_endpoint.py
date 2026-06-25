"""Tests for test_variables_endpoint."""

import pytest

import imednet.endpoints.variables as variables
from imednet.errors import NotFoundError
from imednet.errors.validation import ConfigurationError
from imednet.models.variables import Variable


def test_list_requires_study_key_page_size(
    dummy_client, context, paginator_factory, patch_build_filter
):
    """Test test_list_requires_study_key_page_size behavior."""
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])
    patch = patch_build_filter(variables)

    with pytest.raises(ConfigurationError):
        ep.list()

    result = ep.list(study_key="S1", name="x")

    assert capture["path"] == "/api/v1/edc/studies/S1/variables"
    assert capture["page_size"] == 500
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"name": "x"}
    assert isinstance(result[0], Variable)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test test_get_not_found behavior."""
    ep = variables.VariablesEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, **filters):
        """Test fake_impl behavior."""
        return []

    monkeypatch.setattr(variables.VariablesEndpoint, "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", 1)


def test_list_makes_request_per_call(dummy_client, context, paginator_factory):
    """Test test_list_makes_request_per_call behavior."""
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1")

    assert capture["count"] == 2


def test_list_different_study_keys_make_separate_requests(dummy_client, context, paginator_factory):
    """Test test_list_different_study_keys_make_separate_requests behavior."""
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S2")

    assert capture["count"] == 2
