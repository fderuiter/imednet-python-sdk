"""Tests for the Forms API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.forms import FormsClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
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
    "dateCreated": "2023-01-10T10:00:00Z",
    "dateModified": "2023-01-11T11:00:00Z",
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
    "dateCreated": "2023-02-15T09:00:00Z",
    "dateModified": "2023-02-16T14:30:00Z",
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": FORMS_ENDPOINT,
    "timestamp": datetime.now().isoformat(),
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_FORM_1_DICT, MOCK_FORM_2_DICT],
}


# --- Test Cases ---
@respx.mock
def test_list_forms_success(forms_client):
    """Test successful retrieval of forms list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{FORMS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = forms_client.list_forms(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, FormModel) for item in response.data)
    assert response.data[0].formKey == "FORM_A"
    assert response.data[1].formKey == "FORM_B"


@respx.mock
def test_list_forms_with_params(forms_client):
    """Test list_forms with query parameters."""
    expected_params = {
        "page": "1",
        "size": "10",
        "sort": "formName,desc",
        "filter": 'formType=="Subject"',
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{FORMS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Mock response content doesn't matter here
    )

    forms_client.list_forms(
        study_key=MOCK_STUDY_KEY,
        page=1,
        size=10,
        sort="formName,desc",
        filter='formType=="Subject"',
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "1"
    assert request.url.params["size"] == "10"
    assert request.url.params["sort"] == "formName,desc"
    assert request.url.params["filter"] == 'formType=="Subject"'


def test_list_forms_no_study_key(forms_client):
    """Test list_forms raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        forms_client.list_forms(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        forms_client.list_forms(study_key=None)  # type: ignore
