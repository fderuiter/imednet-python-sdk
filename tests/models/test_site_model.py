"""Tests for site-related data models."""

from datetime import datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from imednet_sdk.models import ApiResponse, SiteModel

# Sample valid data based on docs/reference/sites.md
VALID_SITE_DATA = {
    "studyKey": "PHARMADEMO",
    "siteId": 1,
    "siteName": "Mock Site 1",
    "siteEnrollmentStatus": "Enrollment Open",
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
}

def test_site_creation():
    """Test creating a SiteModel with valid data."""
    site_data = {
        "studyKey": "PHARMADEMO",
        "siteId": 1,
        "siteName": "Mock Site 1",
        "siteEnrollmentStatus": "Enrollment Open",
        "dateCreated": "2024-11-04 16:03:19",
        "dateModified": "2024-11-04 16:03:20",
    }
    site = SiteModel(**site_data)
    assert site.studyKey == "PHARMADEMO"
    assert site.siteId == 1
    assert site.siteName == "Mock Site 1"
    assert site.siteEnrollmentStatus == "Enrollment Open"


def test_site_missing_required_field():
    """Test validation error when required field is missing."""
    site_data = {
        "studyKey": "PHARMADEMO",
        # Missing siteId
        "siteName": "Mock Site 1",
        "siteEnrollmentStatus": "Enrollment Open",
        "dateCreated": "2024-11-04 16:03:19",
        "dateModified": "2024-11-04 16:03:20",
    }
    with pytest.raises(ValidationError):
        SiteModel(**site_data)


def test_site_list_validation():
    """Test validating a list of sites using TypeAdapter."""
    sites_data = [
        {
            "studyKey": "PHARMADEMO",
            "siteId": 1,
            "siteName": "Mock Site 1",
            "siteEnrollmentStatus": "Enrollment Open",
            "dateCreated": "2024-11-04 16:03:19",
            "dateModified": "2024-11-04 16:03:20",
        }
    ]
    adapter = TypeAdapter(list[SiteModel])
    sites = adapter.validate_python(sites_data)
    assert len(sites) == 1
    assert sites[0].siteName == "Mock Site 1"


def test_api_response_with_sites():
    """Test API response containing sites."""
    response_data = {
        "metadata": {
            "status": "OK",
            "method": "GET",
            "path": "/api/v1/edc/studies/PHARMADEMO/sites",
            "timestamp": "2024-11-04 16:03:19",
            "error": {},
        },
        "pagination": {
            "currentPage": 0,
            "size": 25,
            "totalPages": 1,
            "totalElements": 1,
            "sort": [{"property": "siteId", "direction": "ASC"}],
        },
        "data": [
            {
                "studyKey": "PHARMADEMO",
                "siteId": 1,
                "siteName": "Mock Site 1",
                "siteEnrollmentStatus": "Enrollment Open",
                "dateCreated": "2024-11-04 16:03:19",
                "dateModified": "2024-11-04 16:03:20",
            }
        ],
    }
    response = ApiResponse[list[SiteModel]].model_validate(response_data)
    assert response.metadata.status == "OK"
    assert len(response.data) == 1
    assert response.data[0].siteId == 1


def test_site_serialization():
    """Test serializing a site model to JSON/dict."""
    site = SiteModel(
        studyKey="PHARMADEMO",
        siteId=1,
        siteName="Mock Site 1",
        siteEnrollmentStatus="Enrollment Open",
        dateCreated=datetime.fromisoformat("2024-11-04T16:03:19"),
        dateModified=datetime.fromisoformat("2024-11-04T16:03:20"),
    )
    site_dict = site.model_dump()
    assert site_dict["siteId"] == 1
    assert site_dict["siteName"] == "Mock Site 1"

    site_json = site.model_dump(mode="json")
    assert isinstance(site_json["dateCreated"], str)


def test_site_model_validation():
    """Test successful validation of SiteModel with valid data."""
    model = SiteModel.model_validate(VALID_SITE_DATA)

    assert model.studyKey == VALID_SITE_DATA["studyKey"]
    assert model.siteId == VALID_SITE_DATA["siteId"]
    assert model.siteName == VALID_SITE_DATA["siteName"]
    assert model.siteEnrollmentStatus == VALID_SITE_DATA["siteEnrollmentStatus"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 20)


def test_site_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_SITE_DATA.copy()
    del invalid_data["siteName"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        SiteModel.model_validate(invalid_data)

    assert "siteName" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_site_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_SITE_DATA.copy()
    invalid_data["siteId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        SiteModel.model_validate(invalid_data)

    assert "siteId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_datetime = VALID_SITE_DATA.copy()
    invalid_data_datetime["dateCreated"] = "not-a-datetime"
    with pytest.raises(ValidationError) as excinfo_datetime:
        SiteModel.model_validate(invalid_data_datetime)

    assert "dateCreated" in str(excinfo_datetime.value)
    assert "datetime" in str(excinfo_datetime.value).lower()


def test_site_model_serialization():
    """Test serialization of the SiteModel."""
    model = SiteModel.model_validate(VALID_SITE_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_SITE_DATA.copy()
    # Adjust datetime serialization if needed

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateModified"]:
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)
