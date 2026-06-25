"""Tests for test_intervals_endpoint."""

import pytest

import imednet.endpoints.intervals as intervals
from imednet.errors import NotFoundError
from imednet.models.intervals import Interval


def test_list_uses_default_study_and_page_size(
    dummy_client, context, paginator_factory, patch_build_filter
):
    """Test test_list_uses_default_study_and_page_size behavior."""
    context.set_default_study_key("S1")
    ep = intervals.IntervalsEndpoint(dummy_client, context)
    captured = paginator_factory(intervals, [{"intervalId": 1}])
    filter_capture = patch_build_filter(intervals)

    result = ep.list(status="x")

    assert captured["path"] == "/api/v1/edc/studies/S1/intervals"
    assert captured["page_size"] == 500
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "x"}
    assert isinstance(result[0], Interval)


def test_get_not_found(monkeypatch, dummy_client, context):
    """Test test_get_not_found behavior."""
    ep = intervals.IntervalsEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, **filters):
        """Test fake_impl behavior."""
        return []

    monkeypatch.setattr(intervals.IntervalsEndpoint, "_list_sync", fake_impl)

    with pytest.raises(NotFoundError):
        ep.get("S1", 1)


def test_list_makes_request_per_call(dummy_client, context, paginator_factory):
    """Test test_list_makes_request_per_call behavior."""
    ep = intervals.IntervalsEndpoint(dummy_client, context)
    capture = paginator_factory(intervals, [{"intervalId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1")

    assert capture["count"] == 2


def test_list_different_study_keys_make_separate_requests(dummy_client, context, paginator_factory):
    """Test test_list_different_study_keys_make_separate_requests behavior."""
    ep = intervals.IntervalsEndpoint(dummy_client, context)
    capture = paginator_factory(intervals, [{"intervalId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S2")

    assert capture["count"] == 2
