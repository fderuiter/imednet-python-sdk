"""Tests for site-related data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError, TypeAdapter
from imednet_sdk.models import SiteModel, ApiResponse

def test_site_creation():
    """Test creating a SiteModel with valid data."""
    site_data = {
        "studyKey": "PHARMADEMO",
        "siteId": 1,
        "siteName": "Mock Site 1",
        "siteEnrollmentStatus": "Enrollment Open",
        "dateCreated": "2024-11-04 16:03:19",
        "dateModified": "2024-11-04 16:03:20"
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
        "dateModified": "2024-11-04 16:03:20"
    }
    with pytest.raises(ValidationError):
        SiteModel(**site_data)

def test_site_list_validation():
    """Test validating a list of sites using TypeAdapter."""
    sites_data = [{
        "studyKey": "PHARMADEMO",
        "siteId": 1,
        "siteName": "Mock Site 1",
        "siteEnrollmentStatus": "Enrollment Open",
        "dateCreated": "2024-11-04 16:03:19",
        "dateModified": "2024-11-04 16:03:20"
    }]
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
            "error": {}
        },
        "pagination": {
            "currentPage": 0,
            "size": 25,
            "totalPages": 1,
            "totalElements": 1,
            "sort": [{
                "property": "siteId",
                "direction": "ASC"
            }]
        },
        "data": [{
            "studyKey": "PHARMADEMO",
            "siteId": 1,
            "siteName": "Mock Site 1",
            "siteEnrollmentStatus": "Enrollment Open",
            "dateCreated": "2024-11-04 16:03:19",
            "dateModified": "2024-11-04 16:03:20"
        }]
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
        dateModified=datetime.fromisoformat("2024-11-04T16:03:20")
    )
    site_dict = site.model_dump()
    assert site_dict["siteId"] == 1
    assert site_dict["siteName"] == "Mock Site 1"

    site_json = site.model_dump(mode="json")
    assert isinstance(site_json["dateCreated"], str)
