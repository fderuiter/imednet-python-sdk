from datetime import datetime

from imednet.models.records import (
    BaseRecordRequest,
    CreateNewRecordRequest,
    Keyword,
    Record,
    RecordData,
    RecordJobResponse,
    RegisterSubjectRequest,
    UpdateScheduledRecordRequest,
)


def test_keyword():
    data = {
        "keywordName": "test_name",
        "keywordKey": "test_key",
        "keywordId": 123,
        "dateAdded": "2023-01-01T00:00:00",
    }
    keyword = Keyword.from_json(data)
    assert keyword.keyword_name == "test_name"
    assert keyword.keyword_key == "test_key"
    assert keyword.keyword_id == 123
    assert isinstance(keyword.date_added, datetime)


def test_record():
    data = {
        "studyKey": "study1",
        "intervalId": 1,
        "formId": 2,
        "formKey": "form1",
        "siteId": 3,
        "recordId": 4,
        "recordOid": "oid1",
        "recordType": "type1",
        "recordStatus": "status1",
        "deleted": True,
        "dateCreated": "2023-01-01T00:00:00",
        "dateModified": "2023-01-02T00:00:00",
        "subjectId": 5,
        "subjectOid": "soid1",
        "subjectKey": "skey1",
        "visitId": 6,
        "parentRecordId": 7,
        "keywords": [{"keywordName": "k1"}],
        "recordData": {"field1": "value1"},
    }
    record = Record.from_json(data)
    assert record.study_key == "study1"
    assert record.interval_id == 1
    assert record.deleted is True
    assert isinstance(record.keywords[0], Keyword)
    assert record.record_data["field1"] == "value1"


def test_record_job_response():
    data = {"jobId": "job1", "batchId": "batch1", "state": "completed"}
    response = RecordJobResponse.from_json(data)
    assert response.job_id == "job1"
    assert response.batch_id == "batch1"
    assert response.state == "completed"


def test_base_record_request():
    data = {"formKey": "form1", "data": {"field1": "value1"}}
    request = BaseRecordRequest.model_validate(data)
    assert request.form_key == "form1"
    assert isinstance(request.data, RecordData)


def test_register_subject_request():
    data = {"formKey": "form1", "data": {"field1": "value1"}, "siteName": "site1"}
    request = RegisterSubjectRequest.model_validate(data)
    assert request.site_name == "site1"


def test_update_scheduled_record_request():
    data = {
        "formKey": "form1",
        "data": {"field1": "value1"},
        "subjectKey": "subject1",
        "intervalName": "interval1",
    }
    request = UpdateScheduledRecordRequest.model_validate(data)
    assert request.subject_key == "subject1"
    assert request.interval_name == "interval1"


def test_create_new_record_request():
    data = {"formKey": "form1", "data": {"field1": "value1"}, "subjectKey": "subject1"}
    request = CreateNewRecordRequest.model_validate(data)
    assert request.subject_key == "subject1"
