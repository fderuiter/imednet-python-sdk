from unittest.mock import MagicMock

from imednet.models.queries import Query
from imednet.models.records import Record
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.workflows.subject_data import SubjectDataWorkflow


def test_get_all_subject_data_aggregates_across_endpoints() -> None:
    sdk = MagicMock()
    subject = Subject(subject_key="S1")
    visit = Visit(visit_id=1, subject_key="S1")
    record = Record(record_id=1, subject_key="S1", visit_id=1)
    query = Query(query_comments=[])

    sdk.subjects.list.return_value = [subject]
    sdk.visits.list.return_value = [visit]
    sdk.records.list.return_value = [record]
    sdk.queries.list.return_value = [query]

    wf = SubjectDataWorkflow(sdk)
    result = wf.get_all_subject_data("STUDY", "S1")

    sdk.subjects.list.assert_called_once_with("STUDY", filter="subject_key==S1")
    sdk.visits.list.assert_called_once_with("STUDY", filter="subject_key==S1")
    sdk.records.list.assert_called_once_with("STUDY", filter="subject_key==S1")
    sdk.queries.list.assert_called_once_with("STUDY", filter="subject_key==S1")

    assert result.subject_details == subject
    assert result.visits == [visit]
    assert result.records == [record]
    assert result.queries == [query]
