from datetime import datetime

from imednet.models.subjects import Subject, SubjectKeyword


def test_subject_keyword_creation():
    # Test default values
    keyword = SubjectKeyword()
    assert keyword.keyword_name == ""
    assert keyword.keyword_key == ""
    assert keyword.keyword_id == 0
    assert isinstance(keyword.date_added, datetime)

    # Test with data
    data = {
        "keywordName": "test_name",
        "keywordKey": "test_key",
        "keywordId": 123,
        "dateAdded": "2023-01-01T00:00:00",
    }
    keyword = SubjectKeyword.from_json(data)
    assert keyword.keyword_name == "test_name"
    assert keyword.keyword_key == "test_key"
    assert keyword.keyword_id == 123
    assert keyword.date_added == datetime(2023, 1, 1)


def test_subject_creation():
    # Test default values
    subject = Subject()
    assert subject.study_key == ""
    assert subject.subject_id == 0
    assert subject.subject_oid == ""
    assert subject.subject_key == ""
    assert subject.subject_status == ""
    assert subject.site_id == 0
    assert subject.site_name == ""
    assert subject.deleted is False
    assert isinstance(subject.enrollment_start_date, datetime)
    assert isinstance(subject.date_created, datetime)
    assert isinstance(subject.date_modified, datetime)
    assert subject.keywords == []

    # Test with data
    data = {
        "studyKey": "study1",
        "subjectId": 1,
        "subjectOid": "oid1",
        "subjectKey": "key1",
        "subjectStatus": "active",
        "siteId": 100,
        "siteName": "Site A",
        "deleted": True,
        "enrollmentStartDate": "2023-01-01T00:00:00",
        "dateCreated": "2023-01-01T00:00:00",
        "dateModified": "2023-01-02T00:00:00",
        "keywords": [
            {
                "keywordName": "test_kw",
                "keywordKey": "key_kw",
                "keywordId": 1,
                "dateAdded": "2023-01-01T00:00:00",
            }
        ],
    }
    subject = Subject.from_json(data)
    assert subject.study_key == "study1"
    assert subject.subject_id == 1
    assert subject.subject_oid == "oid1"
    assert subject.subject_key == "key1"
    assert subject.subject_status == "active"
    assert subject.site_id == 100
    assert subject.site_name == "Site A"
    assert subject.deleted is True
    assert subject.enrollment_start_date == datetime(2023, 1, 1)
    assert subject.date_created == datetime(2023, 1, 1)
    assert subject.date_modified == datetime(2023, 1, 2)
    assert len(subject.keywords) == 1
    assert isinstance(subject.keywords[0], SubjectKeyword)
