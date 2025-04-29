from datetime import datetime

from imednet.models.sites import Site


def test_site_creation_with_defaults():
    site = Site()
    assert site.study_key == ""
    assert site.site_id == 0
    assert site.site_name == ""
    assert site.site_enrollment_status == ""
    assert isinstance(site.date_created, datetime)
    assert isinstance(site.date_modified, datetime)


def test_site_creation_with_values():
    data = {
        "studyKey": "STUDY1",
        "siteId": 123,
        "siteName": "Test Site",
        "siteEnrollmentStatus": "ACTIVE",
        "dateCreated": "2023-01-01T00:00:00",
        "dateModified": "2023-01-02T00:00:00",
    }
    site = Site.from_json(data)
    assert site.study_key == "STUDY1"
    assert site.site_id == 123
    assert site.site_name == "Test Site"
    assert site.site_enrollment_status == "ACTIVE"
    assert site.date_created == datetime(2023, 1, 1, 0, 0, 0)
    assert site.date_modified == datetime(2023, 1, 2, 0, 0, 0)


def test_site_creation_with_field_names():
    data = {
        "study_key": "STUDY1",
        "site_id": 123,
        "site_name": "Test Site",
        "site_enrollment_status": "ACTIVE",
        "date_created": "2023-01-01T00:00:00",
        "date_modified": "2023-01-02T00:00:00",
    }
    site = Site.from_json(data)
    assert site.study_key == "STUDY1"
    assert site.site_id == 123
    assert site.site_name == "Test Site"
    assert site.site_enrollment_status == "ACTIVE"
    assert site.date_created == datetime(2023, 1, 1, 0, 0, 0)
    assert site.date_modified == datetime(2023, 1, 2, 0, 0, 0)


def test_site_creation_with_invalid_values():
    data = {
        "studyKey": None,
        "siteId": None,
        "siteName": None,
        "siteEnrollmentStatus": None,
        "dateCreated": None,
        "dateModified": None,
    }
    site = Site.from_json(data)
    assert site.study_key == ""
    assert site.site_id == 0
    assert site.site_name == ""
    assert site.site_enrollment_status == ""
    assert isinstance(site.date_created, datetime)
    assert isinstance(site.date_modified, datetime)
