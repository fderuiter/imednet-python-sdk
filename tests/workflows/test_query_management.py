from unittest.mock import MagicMock

from imednet.api.models.queries import Query, QueryComment
from imednet.api.models.subjects import Subject
from imednet.testing import fake_data
from imednet.workflows.query_management import QueryManagementWorkflow


def make_query(sequence_closed: list[tuple[int, bool]]) -> Query:
    comments = [QueryComment(sequence=seq, closed=closed) for seq, closed in sequence_closed]
    return Query(query_comments=comments)


def test_get_open_queries_filters_latest_comment() -> None:
    sdk = MagicMock()
    query_closed = make_query([(1, False), (2, True)])
    query_open = make_query([(1, False)])
    query_unknown = make_query([])
    sdk.queries.list.return_value = [query_closed, query_open, query_unknown]

    wf = QueryManagementWorkflow(sdk)
    result = wf.get_open_queries("STUDY", additional_filter={"state": "new"})

    sdk.queries.list.assert_called_once_with("STUDY", state="new")
    assert sdk.queries.list.call_args.kwargs == {"state": "new"}
    assert result == [query_open]


def test_get_queries_for_subject_builds_combined_filter() -> None:
    sdk = MagicMock()
    wf = QueryManagementWorkflow(sdk)
    wf.get_queries_for_subject("STUDY", "SUBJ1", additional_filter={"type": "x"})

    sdk.queries.list.assert_called_once_with("STUDY", subject_key="SUBJ1", type="x")
    assert sdk.queries.list.call_args.kwargs == {"subject_key": "SUBJ1", "type": "x"}


def test_get_query_state_counts_aggregates_states() -> None:
    sdk = MagicMock()
    open_query = make_query([(1, False)])
    closed_query = make_query([(1, True)])
    unknown_query = make_query([])
    sdk.queries.list.return_value = [open_query, closed_query, unknown_query]

    wf = QueryManagementWorkflow(sdk)
    counts = wf.get_query_state_counts("STUDY")

    sdk.queries.list.assert_called_once_with("STUDY")
    assert sdk.queries.list.call_args.kwargs == {}
    assert counts == {"open": 1, "closed": 1, "unknown": 1}


def test_get_queries_by_site_filters_using_subjects() -> None:
    sdk = MagicMock()
    s1 = Subject.from_json(fake_data.fake_subject())
    s2 = Subject.from_json(fake_data.fake_subject())
    s1.subject_key = "S1"
    s2.subject_key = "S2"
    sdk.subjects.list.return_value = [s1, s2]
    wf = QueryManagementWorkflow(sdk)

    wf.get_queries_by_site("STUDY", "SITE", additional_filter={"state": "open"})

    sdk.subjects.list.assert_called_once_with("STUDY", site_name="SITE")
    sdk.queries.list.assert_called_once_with("STUDY", subject_key=["S1", "S2"], state="open")
    assert sdk.queries.list.call_args.kwargs == {"subject_key": ["S1", "S2"], "state": "open"}


def test_get_queries_by_site_returns_empty_if_no_subjects() -> None:
    sdk = MagicMock()
    sdk.subjects.list.return_value = []
    wf = QueryManagementWorkflow(sdk)

    result = wf.get_queries_by_site("STUDY", "SITE")

    sdk.subjects.list.assert_called_once_with("STUDY", site_name="SITE")
    sdk.queries.list.assert_not_called()
    assert result == []


def test_get_queries_by_site_with_space_in_name() -> None:
    sdk = MagicMock()
    s = Subject.from_json(fake_data.fake_subject())
    s.subject_key = "S1"
    sdk.subjects.list.return_value = [s]
    wf = QueryManagementWorkflow(sdk)

    wf.get_queries_by_site("STUDY", "Mock Site")

    sdk.subjects.list.assert_called_once_with("STUDY", site_name="Mock Site")
    sdk.queries.list.assert_called_once_with("STUDY", subject_key=["S1"])
    assert sdk.queries.list.call_args.kwargs == {"subject_key": ["S1"]}


def test_get_queries_by_site_intersects_subject_filters() -> None:
    """Test that subject_key in additional_filter is intersected with site subjects."""
    sdk = MagicMock()
    s1 = Subject.from_json(fake_data.fake_subject())
    s1.subject_key = "S1"
    s2 = Subject.from_json(fake_data.fake_subject())
    s2.subject_key = "S2"
    sdk.subjects.list.return_value = [s1, s2]  # Subjects in the site are S1, S2
    wf = QueryManagementWorkflow(sdk)

    # Filter asks for subjects S2, S3. The intersection is just S2.
    additional_filter = {"subject_key": ["S2", "S3"], "state": "open"}
    wf.get_queries_by_site("STUDY", "SITE", additional_filter=additional_filter)

    sdk.subjects.list.assert_called_once_with("STUDY", site_name="SITE")

    sdk.queries.list.assert_called_once_with("STUDY", subject_key=["S2"], state="open")


def test_get_queries_by_site_intersects_single_subject_filter() -> None:
    """Test that a single subject_key string is handled correctly."""
    sdk = MagicMock()
    s1 = Subject.from_json(fake_data.fake_subject())
    s1.subject_key = "S1"
    s2 = Subject.from_json(fake_data.fake_subject())
    s2.subject_key = "S2"
    sdk.subjects.list.return_value = [s1, s2]  # Subjects in the site are S1, S2
    wf = QueryManagementWorkflow(sdk)

    # Filter asks for subject S1. The intersection is just S1.
    additional_filter = {"subject_key": "S1", "state": "open"}
    wf.get_queries_by_site("STUDY", "SITE", additional_filter=additional_filter)

    sdk.subjects.list.assert_called_once_with("STUDY", site_name="SITE")

    sdk.queries.list.assert_called_once_with("STUDY", subject_key=["S1"], state="open")
