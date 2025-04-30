from datetime import datetime

from imednet.models.studies import Study


def test_study_default_values():
    study = Study()
    assert study.sponsor_key == ""
    assert study.study_key == ""
    assert study.study_id == 0
    assert study.study_name == ""
    assert study.study_description == ""
    assert study.study_type == ""
    assert isinstance(study.date_created, datetime)
    assert isinstance(study.date_modified, datetime)


def test_study_with_values():
    data = {
        "sponsorKey": "SP123",
        "studyKey": "ST456",
        "studyId": 789,
        "studyName": "Test Study",
        "studyDescription": "Test Description",
        "studyType": "Clinical",
        "dateCreated": "2023-01-01T00:00:00",
        "dateModified": "2023-01-02T00:00:00",
    }
    study = Study(**data)
    assert study.sponsor_key == "SP123"
    assert study.study_key == "ST456"
    assert study.study_id == 789
    assert study.study_name == "Test Study"
    assert study.study_description == "Test Description"
    assert study.study_type == "Clinical"
    assert study.date_created == datetime(2023, 1, 1, 0, 0, 0)
    assert study.date_modified == datetime(2023, 1, 2, 0, 0, 0)


def test_study_field_validation():
    data = {
        "sponsorKey": None,
        "studyKey": None,
        "studyId": None,
        "studyName": None,
        "studyDescription": None,
        "studyType": None,
        "dateCreated": None,
        "dateModified": None,
    }
    study = Study(**data)
    assert study.sponsor_key == ""
    assert study.study_key == ""
    assert study.study_id == 0
    assert study.study_name == ""
    assert study.study_description == ""
    assert study.study_type == ""
    assert isinstance(study.date_created, datetime)
    assert isinstance(study.date_modified, datetime)
