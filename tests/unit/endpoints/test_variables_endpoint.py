import pytest

import imednet.endpoints.variables as variables
from imednet.models.variables import Variable


def test_list_requires_study_key_page_size(
    dummy_client, context, paginator_factory, patch_build_filter
):
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])
    patch = patch_build_filter(variables)

    with pytest.raises(KeyError):
        ep.list()

    result = ep.list(study_key="S1", name="x")

    assert capture["path"] == "/api/v1/edc/studies/S1/variables"
    assert capture["page_size"] == 500
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"name": "x"}
    assert isinstance(result[0], Variable)


def test_get_not_found(monkeypatch, dummy_client, context):
    ep = variables.VariablesEndpoint(dummy_client, context)

    def fake_impl(self, client, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(variables.VariablesEndpoint, "_list_sync", fake_impl)

    with pytest.raises(ValueError):
        ep.get("S1", 1)


def test_list_caches_by_study_key(dummy_client, context, paginator_factory):
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])

    first = ep.list(study_key="S1")
    second = ep.list(study_key="S1")

    assert capture["count"] == 1
    assert first == second

    ep.list(study_key="S2")

    assert capture["count"] == 2


def test_list_refresh_bypasses_cache(dummy_client, context, paginator_factory):
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1", refresh=True)

    assert capture["count"] == 2
