from datetime import datetime

import pytest
from imednet.models.record_revisions import RecordRevision


def test_record_revision_default_values():
    revision = RecordRevision()
    assert revision.study_key == ""
    assert revision.record_revision_id == 0
    assert revision.record_id == 0
    assert revision.record_oid == ""
    assert revision.record_revision == 0
    assert revision.data_revision == 0
    assert revision.record_status == ""
    assert revision.subject_id == 0
    assert revision.subject_oid == ""
    assert revision.subject_key == ""
    assert revision.site_id == 0
    assert revision.form_key == ""
    assert revision.interval_id == 0
    assert revision.role == ""
    assert revision.user == ""
    assert revision.reason_for_change == ""
    assert revision.deleted is False
    assert isinstance(revision.date_created, datetime)


def test_record_revision_from_json():
    test_data = {
        "studyKey": "STUDY1",
        "recordRevisionId": "123",
        "recordId": "456",
        "recordOid": "R1",
        "recordRevision": "1",
        "dataRevision": "2",
        "recordStatus": "COMPLETE",
        "subjectId": "789",
        "subjectOid": "S1",
        "subjectKey": "SK1",
        "siteId": "10",
        "formKey": "F1",
        "intervalId": "1",
        "role": "INVESTIGATOR",
        "user": "testuser",
        "reasonForChange": "update",
        "deleted": "true",
        "dateCreated": "2023-01-01T12:00:00",
    }

    revision = RecordRevision.from_json(test_data)

    assert revision.study_key == "STUDY1"
    assert revision.record_revision_id == 123
    assert revision.record_id == 456
    assert revision.record_oid == "R1"
    assert revision.record_revision == 1
    assert revision.data_revision == 2
    assert revision.record_status == "COMPLETE"
    assert revision.subject_id == 789
    assert revision.subject_oid == "S1"
    assert revision.subject_key == "SK1"
    assert revision.site_id == 10
    assert revision.form_key == "F1"
    assert revision.interval_id == 1
    assert revision.role == "INVESTIGATOR"
    assert revision.user == "testuser"
    assert revision.reason_for_change == "update"
    assert revision.deleted is True
    assert revision.date_created == datetime(2023, 1, 1, 12, 0)


def test_record_revision_invalid_data():
    with pytest.raises(ValueError):
        RecordRevision.from_json({"recordRevisionId": "invalid", "dateCreated": "invalid-date"})
