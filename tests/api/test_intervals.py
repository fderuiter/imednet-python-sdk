"""Tests for the Intervals API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.intervals import IntervalsClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.models.interval import IntervalFormModel, IntervalModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "TEST_STUDY"
INTERVALS_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/intervals"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def intervals_client(client):
    """Fixture for IntervalsClient."""
    return IntervalsClient(client)


# --- Mock Data ---
MOCK_INTERVAL_FORM_1 = {
    "formId": 101,
    "formKey": "VISIT_FORM_1",
    "formName": "Visit Form 1",
}
MOCK_INTERVAL_FORM_2 = {
    "formId": 102,
    "formKey": "VISIT_FORM_2",
    "formName": "Visit Form 2",
}

MOCK_INTERVAL_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "intervalId": 1,
    "intervalName": "Screening",
    "intervalDescription": "Initial screening visit",
    "intervalSequence": 1,
    "intervalGroupId": 10,
    "intervalGroupName": "Group A",
    "timeline": "Baseline",
    "definedUsingInterval": None,
    "windowCalculationForm": None,
    "windowCalculationDate": None,
    "actualDateForm": "DEMOGRAPHICS",
    "actualDate": "VISIT_DATE",
    "dueDateWillBeIn": None,
    "negativeSlack": None,
    "positiveSlack": None,
    "eproGracePeriod": None,
    "forms": [MOCK_INTERVAL_FORM_1],
    "disabled": False,
    "dateCreated": "2023-03-01T10:00:00Z",
    "dateModified": "2023-03-02T11:00:00Z",
}
MOCK_INTERVAL_2_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "intervalId": 2,
    "intervalName": "Visit 1",
    "intervalDescription": "First follow-up visit",
    "intervalSequence": 2,
    "intervalGroupId": 10,
    "intervalGroupName": "Group A",
    "timeline": "Calculated",
    "definedUsingInterval": "Screening",
    "windowCalculationForm": "DEMOGRAPHICS",
    "windowCalculationDate": "VISIT_DATE",
    "actualDateForm": "VISIT_1_FORM",
    "actualDate": "VISIT_1_DATE",
    "dueDateWillBeIn": 7,
    "negativeSlack": 2,
    "positiveSlack": 2,
    "eproGracePeriod": 3,
    "forms": [MOCK_INTERVAL_FORM_2],
    "disabled": False,
    "dateCreated": "2023-03-05T09:00:00Z",
    "dateModified": "2023-03-06T14:30:00Z",
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "path": INTERVALS_ENDPOINT,
    "timestamp": datetime.now().isoformat(),
    "pagination": {"page": 0, "size": 2, "total": 2},
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "data": [MOCK_INTERVAL_1_DICT, MOCK_INTERVAL_2_DICT],
}


# --- Test Cases ---
@respx.mock
def test_list_intervals_success(intervals_client):
    """Test successful retrieval of intervals list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{INTERVALS_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = intervals_client.list_intervals(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.metadata.pagination, PaginationInfo)
    assert response.metadata.status == "OK"
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert all(isinstance(item, IntervalModel) for item in response.data)
    assert response.data[0].intervalName == "Screening"
    assert response.data[1].intervalName == "Visit 1"
    assert isinstance(response.data[0].forms, list)
    assert len(response.data[0].forms) == 1
    assert isinstance(response.data[0].forms[0], IntervalFormModel)
    assert response.data[0].forms[0].formKey == "VISIT_FORM_1"


@respx.mock
def test_list_intervals_with_params(intervals_client):
    """Test list_intervals with query parameters."""
    expected_params = {
        "page": "2",
        "size": "5",
        "sort": "intervalSequence,desc",
        "filter": 'intervalGroupName=="Group B"',
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{INTERVALS_ENDPOINT}", params=expected_params).mock(
        return_value=Response(
            200, json=MOCK_SUCCESS_RESPONSE_DICT
        )  # Mock response content doesn't matter here
    )

    intervals_client.list_intervals(
        study_key=MOCK_STUDY_KEY,
        page=2,
        size=5,
        sort="intervalSequence,desc",
        filter='intervalGroupName=="Group B"',
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "2"
    assert request.url.params["size"] == "5"
    assert request.url.params["sort"] == "intervalSequence,desc"
    assert request.url.params["filter"] == 'intervalGroupName=="Group B"'


def test_list_intervals_no_study_key(intervals_client):
    """Test list_intervals raises ValueError if study_key is missing."""
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        intervals_client.list_intervals(study_key="")
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        intervals_client.list_intervals(study_key=None)  # type: ignore
