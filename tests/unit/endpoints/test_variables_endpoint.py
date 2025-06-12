import pytest

import imednet.endpoints.variables as variables
from imednet.models.variables import Variable


def test_list_requires_study_key_page_size(dummy_client, context, paginator_factory, patch_build_filter):
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


def test_get_not_found(dummy_client, context, response_factory):
    ep = variables.VariablesEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("S1", 1)
