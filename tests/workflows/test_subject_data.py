from unittest.mock import MagicMock

from imednet.models.queries import Query
from imednet.models.records import Record
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.testing import fake_data
from imednet.workflows.subject_data import SubjectDataWorkflow


def test_get_all_subject_data_aggregates_across_endpoints(schema) -> None:
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

    sdk.subjects.list.return_value = [subject]
    sdk.visits.list.return_value = [visit]
    sdk.records.list.return_value = [record]
    sdk.queries.list.return_value = [query]

    wf = SubjectDataWorkflow(sdk)
    result = wf.get_all_subject_data("STUDY", "S1")

    sdk.subjects.list.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.subjects.list.call_args.kwargs == {"subject_key": "S1"}
    sdk.visits.list.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.visits.list.call_args.kwargs == {"subject_key": "S1"}
    sdk.records.list.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.records.list.call_args.kwargs == {"subject_key": "S1"}
    sdk.queries.list.assert_called_once_with("STUDY", subject_key="S1")
    assert sdk.queries.list.call_args.kwargs == {"subject_key": "S1"}

    assert result.subject_details == subject
    assert result.visits == [visit]
    assert result.records == [record]
    assert result.queries == [query]
