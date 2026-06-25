"""Tests for test_subject_data."""

from unittest.mock import MagicMock

from imednet.models.queries import Query
from imednet.models.records import Record
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.testing import fake_data
from imednet_workflows.subject_data import SubjectComprehensiveData, SubjectDataWorkflow


def test_get_all_subject_data_aggregates_across_endpoints(schema) -> None:
    """Test test_get_all_subject_data_aggregates_across_endpoints behavior."""
    sdk = MagicMock()
    subject = Subject.from_json(fake_data.fake_subject())
    visit = Visit.from_json(fake_data.fake_visit())
    record_dict = fake_data.fake_record(schema)
    record = Record.from_json(record_dict)
    query = Query.from_json(fake_data.fake_query())

    subject.subject_key = "S1"
    visit.subject_key = "S1"
    visit.visit_id = 1
    record.subject_key = "S1"
    record.visit_id = 1

    sdk.get_subjects.return_value = [subject]
    sdk.get_visits.return_value = [visit]
    sdk.get_records.return_value = [record]
    sdk.get_queries.return_value = [query]

    wf = SubjectDataWorkflow(sdk)
    result = wf.get_all_subject_data("STUDY", "S1")

    sdk.get_subjects.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.get_subjects.call_args.kwargs == {"subject_key": "S1"}
    sdk.get_visits.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.get_visits.call_args.kwargs == {"subject_key": "S1"}
    sdk.get_records.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.get_records.call_args.kwargs == {"subject_key": "S1"}
    sdk.get_queries.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.get_queries.call_args.kwargs == {"subject_key": "S1"}

    assert result.subject_details == subject
    assert result.visits == [visit]
    assert result.records == [record]
    assert result.queries == [query]


def test_get_all_subject_data_returns_empty_results() -> None:
    """Test test_get_all_subject_data_returns_empty_results behavior."""
    sdk = MagicMock()
    sdk.get_subjects.return_value = []
    sdk.get_visits.return_value = []
    sdk.get_records.return_value = []
    sdk.get_queries.return_value = []

    wf = SubjectDataWorkflow(sdk)
    result = wf.get_all_subject_data("STUDY", "S2")

    sdk.get_subjects.assert_called_once_with("STUDY", subject_key="S2")
    assert sdk.get_subjects.call_args.kwargs == {"subject_key": "S2"}
    sdk.get_visits.assert_called_once_with("STUDY", subject_key="S2")
    assert sdk.get_visits.call_args.kwargs == {"subject_key": "S2"}
    sdk.get_records.assert_called_once_with("STUDY", subject_key="S2")
    assert sdk.get_records.call_args.kwargs == {"subject_key": "S2"}
    sdk.get_queries.assert_called_once_with("STUDY", subject_key="S2")
    assert sdk.get_queries.call_args.kwargs == {"subject_key": "S2"}

    assert isinstance(result, SubjectComprehensiveData)
    assert result.subject_details is None
    assert result.visits == []
    assert result.records == []
    assert result.queries == []
