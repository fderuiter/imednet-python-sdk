"""Tests for the Forms API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.forms import FormsClient
from imednet_sdk.client import ImednetClient
# Use PaginationInfo based on _common.py
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo, SortInfo
from imednet_sdk.models.form import FormModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
FORMS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/forms"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def forms_client(client):
    """Fixture for FormsClient."""
    return FormsClient(client)


# --- Mock Data ---
MOCK_FORM_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "formId": 1,
    "formKey": "FORM_A",
    "formName": "Form A",
    "formType": "Subject",
    "revision": 2,
    "embeddedLog": False,
    "enforceOwnership": False,
    "userAgreement": False,
    "subjectRecordReport": False,
    "unscheduledVisit": False,
    "otherForms": False,
    "eproForm": False,
    "allowCopy": True,
    "disabled": False,
    # Use format consistent with docs example
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
}
MOCK_FORM_2_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "formId": 2,
    "formKey": "FORM_B",
    "formName": "Form B",
    "formType": "Site",
    "revision": 1,
    "embeddedLog": True,
    "enforceOwnership": True,
    "userAgreement": False,
    "subjectRecordReport": True,
    "unscheduledVisit": True,
    "otherForms": True,
    "eproForm": True,
    "allowCopy": False,
    "disabled": True,
    "dateCreated": "2024-11-05 09:00:00",
    "dateModified": "2024-11-05 14:30:00",
}

# Corrected Metadata based on docs (no nested pagination)
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method as per docs
    "path": FORMS_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp for consistency
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 2,
    "totalPages": 1,
    "totalElements": 2,
    "sort": [{"property": "formId", "direction": "ASC"}],  # Use 'property' as per docs
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_FORM_1_DICT, MOCK_FORM_2_DICT],
}


# --- Test Cases ---
@respx.mock
def test_list_forms_success(forms_client, client):
    """Test successful retrieval of forms list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{FORMS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = forms_client.list_forms(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert isinstance(response.data, list)
    assert response.metadata.status == "OK"
    assert response.metadata.path == FORMS_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 2
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 2
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "formId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, FormModel) for item in response.data)
    assert response.data[0].formKey == "FORM_A"
    assert response.data[1].formKey == "FORM_B"
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")


@respx.mock
def test_list_forms_with_params(forms_client, client):
    """Test list_forms with query parameters."""
    # Use filter syntax from docs example (==)
    params = {
        "page": 1,
        "size": 10,
        "sort": "formName,desc",
        "filter": "formType==Subject",
    }
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{FORMS_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 1,
        "size": 10,
        "totalPages": 1,
        "totalElements": 1,
        "sort": [{"property": "formName", "direction": "DESC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [MOCK_FORM_1_DICT],
    }  # Example data

    # Ensure respx matches the exact params
    expected_params = {
        "page": "1",
        "size": "10",
        "sort": "formName,desc",
        "filter": "formType==Subject",
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{FORMS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = forms_client.list_forms(
        study_key=MOCK_STUDY_KEY,
        page=1,
        size=10,
        sort="formName,desc",
        filter="formType==Subject",
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "1"
    assert request.url.params["size"] == "10"
    assert request.url.params["sort"] == "formName,desc"
    assert request.url.params["filter"] == "formType==Subject"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 10
    assert response.pagination.sort[0].property == "formName"
    assert response.pagination.sort[0].direction == "DESC"
    assert isinstance(response.data, list)


def test_list_forms_no_study_key(forms_client):
    """Test list_forms raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        forms_client.list_forms(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        forms_client.list_forms(study_key=None)  # type: ignore
