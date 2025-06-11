import datetime

from imednet.models.sites import Site


def test_site_model_validate_aliases() -> None:
    data = {
        "studyKey": "S1",
        "siteId": 1,
        "siteName": "Site A",
        "siteEnrollmentStatus": "ACTIVE",
        "dateCreated": "2024-01-01T12:00:00Z",
        "dateModified": "2024-01-02T12:00:00Z",
    }
    site = Site.model_validate(data)
    assert site.study_key == "S1"
    assert site.site_id == 1
    assert site.site_name == "Site A"
    assert site.site_enrollment_status == "ACTIVE"
    assert site.date_created == datetime.datetime(
        2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert site.date_modified == datetime.datetime(
        2024, 1, 2, 12, 0, 0, tzinfo=datetime.timezone.utc
    )


def test_site_model_validate_field_names() -> None:
    data = {
        "study_key": "S1",
        "site_id": 2,
        "site_name": "Site B",
        "site_enrollment_status": "OPEN",
    }
    site = Site.model_validate(data)
    assert site.site_id == 2
    assert site.study_key == "S1"
    assert site.site_name == "Site B"
    assert site.site_enrollment_status == "OPEN"
