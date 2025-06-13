from unittest.mock import MagicMock

from imednet.models.record_revisions import RecordRevision
from imednet.models.records import Record
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.workflows.data_extraction import DataExtractionWorkflow


def test_extract_records_by_criteria_filters_subject_and_visit() -> None:
    sdk = MagicMock()
    sdk.subjects.list.return_value = [Subject(subject_key="S1"), Subject(subject_key="S2")]
    sdk.visits.list.return_value = [
        Visit(visit_id=1, subject_key="S1"),
        Visit(visit_id=2, subject_key="S2"),
    ]
    records = [
        Record(record_id=1, subject_key="S1", visit_id=1),
        Record(record_id=2, subject_key="S2", visit_id=2),
        Record(record_id=3, subject_key="S1", visit_id=99),
    ]
    sdk.records.list.return_value = records

    wf = DataExtractionWorkflow(sdk)
    result = wf.extract_records_by_criteria(
        "STUDY",
        subject_filter={"status": "active"},
        visit_filter={"visit_id": 1},
    )

    sdk.subjects.list.assert_called_once_with("STUDY", status="active")
    sdk.visits.list.assert_called_once_with("STUDY", visit_id=1)
    sdk.records.list.assert_called_once_with(study_key="STUDY", record_data_filter=None)

    assert [r.record_id for r in result] == [1, 2]


def test_extract_audit_trail_builds_filters_and_dates() -> None:
    sdk = MagicMock()
    revisions = [RecordRevision(record_revision_id=1)]
    sdk.record_revisions.list.return_value = revisions

    wf = DataExtractionWorkflow(sdk)
    result = wf.extract_audit_trail(
        "STUDY",
        start_date="2021-01-01",
        end_date="2021-01-02",
        user_filter={"role": "data"},
        status="open",
    )

    sdk.record_revisions.list.assert_called_once_with(
        "STUDY",
        role="data",
        status="open",
        start_date="2021-01-01",
        end_date="2021-01-02",
    )
    assert result == revisions
