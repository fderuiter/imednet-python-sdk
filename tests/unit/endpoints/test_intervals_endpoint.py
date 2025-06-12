import imednet.endpoints.intervals as intervals
import pytest
from imednet.models.intervals import Interval


def test_list_uses_default_study_and_page_size(
    dummy_client, context, paginator_factory, patch_build_filter
):
    context.set_default_study_key("S1")
    ep = intervals.IntervalsEndpoint(dummy_client, context)
    captured = paginator_factory(intervals, [{"intervalId": 1}])
    filter_capture = patch_build_filter(intervals)

    result = ep.list(status="x")

    assert captured["path"] == "/api/v1/edc/studies/S1/intervals"
    assert captured["page_size"] == 500
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "x", "studyKey": "S1"}
    assert isinstance(result[0], Interval)


def test_get_not_found(dummy_client, context, response_factory):
    ep = intervals.IntervalsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("S1", 1)


def test_list_caches_by_study_key(dummy_client, context, paginator_factory):
    ep = intervals.IntervalsEndpoint(dummy_client, context)
    capture = paginator_factory(intervals, [{"intervalId": 1}])

    first = ep.list(study_key="S1")
    second = ep.list(study_key="S1")

    assert capture["count"] == 1
    assert first == second

    ep.list(study_key="S2")

    assert capture["count"] == 2


def test_list_refresh_bypasses_cache(dummy_client, context, paginator_factory):
    ep = intervals.IntervalsEndpoint(dummy_client, context)
    capture = paginator_factory(intervals, [{"intervalId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1", refresh=True)

    assert capture["count"] == 2
