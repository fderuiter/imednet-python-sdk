from unittest.mock import MagicMock

from imednet.api.models.record_revisions import RecordRevision
from imednet.api.models.records import Record
from imednet.api.models.subjects import Subject
from imednet.api.models.visits import Visit
from imednet.testing import fake_data
from imednet.workflows.data_extraction import DataExtractionWorkflow


def test_extract_records_by_criteria_filters_subject_and_visit(schema) -> None:
    sdk = MagicMock()
    s1 = Subject.from_json(fake_data.fake_subject())
    s2 = Subject.from_json(fake_data.fake_subject())
    s1.subject_key = "S1"
    s2.subject_key = "S2"
    sdk.subjects.list.return_value = [s1, s2]

    v1 = Visit.from_json(fake_data.fake_visit())
    v2 = Visit.from_json(fake_data.fake_visit())
    v1.subject_key = "S1"
    v1.visit_id = 1
    v2.subject_key = "S2"
    v2.visit_id = 2
    sdk.visits.list.return_value = [v1, v2]

    r1 = Record.from_json(fake_data.fake_record(schema))
    r2 = Record.from_json(fake_data.fake_record(schema))
    r3 = Record.from_json(fake_data.fake_record(schema))
    r1.subject_key = "S1"
    r1.visit_id = 1
    r1.record_id = 1
    r2.subject_key = "S2"
    r2.visit_id = 2
    r2.record_id = 2
    r3.subject_key = "S1"
    r3.visit_id = 99
    r3.record_id = 3
    sdk.records.list.return_value = [r1, r2, r3]

    wf = DataExtractionWorkflow(sdk)
    result = wf.extract_records_by_criteria(
        "STUDY",
        subject_filter={"status": "active"},
        visit_filter={"visit_id": 1},
    )

    sdk.subjects.list.assert_called_once_with("STUDY", status="active")
    assert sdk.subjects.list.call_args.kwargs == {"status": "active"}
    sdk.visits.list.assert_called_once_with("STUDY", visit_id=1)
    assert sdk.visits.list.call_args.kwargs == {"visit_id": 1}
    sdk.records.list.assert_called_once_with(study_key="STUDY", record_data_filter=None)
    assert sdk.records.list.call_args.kwargs == {"study_key": "STUDY", "record_data_filter": None}

    assert [r.record_id for r in result] == [1, 2]


def test_extract_audit_trail_builds_filters_and_dates() -> None:
    sdk = MagicMock()
    revision = RecordRevision.from_json(fake_data.fake_record_revision())
    sdk.record_revisions.list.return_value = [revision]

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
    assert result == [revision]
