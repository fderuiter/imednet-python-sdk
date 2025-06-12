import pytest

import imednet.endpoints.visits as visits
from imednet.models.visits import Visit


def test_list_filters_and_path(dummy_client, context, paginator_factory, patch_build_filter):
    context.set_default_study_key("S1")
    ep = visits.VisitsEndpoint(dummy_client, context)
    capture = paginator_factory(visits, [{"visitId": 1}])
    patch = patch_build_filter(visits)

    result = ep.list(status="x")

    assert capture["path"] == "/api/v1/edc/studies/S1/visits"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "x", "studyKey": "S1"}
    assert isinstance(result[0], Visit)


def test_get_not_found(dummy_client, context, response_factory):
    ep = visits.VisitsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("S1", 1)
