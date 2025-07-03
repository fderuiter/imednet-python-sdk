import imednet.endpoints.visits as visits
import pytest
from imednet.models.visits import Visit


def test_list_filters_and_path(dummy_client, context, paginator_factory, patch_build_filter):
    context.set_default_study_key("S1")
    ep = visits.VisitsEndpoint(dummy_client, context)
    capture = paginator_factory(visits, [{"visitId": 1}])
    patch = patch_build_filter(visits)

    result = ep.list(status="x")

    assert capture["path"] == "/api/v1/edc/studies/S1/visits"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "x"}
    assert isinstance(result[0], Visit)


def test_get_not_found(monkeypatch, dummy_client, context):
    ep = visits.VisitsEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(visits.VisitsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        ep.get("S1", 1)
