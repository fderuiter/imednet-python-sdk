import imednet.endpoints.queries as queries
import pytest
from imednet.models.queries import Query


def test_list_builds_path_and_filters(dummy_client, context, paginator_factory, patch_build_filter):
    context.set_default_study_key("S1")
    ep = queries.QueriesEndpoint(dummy_client, context)
    capture = paginator_factory(queries, [{"annotationId": 1}])
    patch = patch_build_filter(queries)

    result = ep.list(status="new")

    assert capture["path"] == "/api/v1/edc/studies/S1/queries"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"status": "new"}
    assert isinstance(result[0], Query)


def test_get_not_found(monkeypatch, dummy_client, context):
    ep = queries.QueriesEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(queries.QueriesEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        ep.get("S1", 1)
