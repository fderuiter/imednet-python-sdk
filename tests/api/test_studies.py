"""Tests for the Studies API client."""

import urllib.parse  # Added for URL encoding/parsing
from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.studies import StudiesClient
from imednet_sdk.client import ImednetClient
from imednet_sdk.exceptions import (ApiError, AuthenticationError, AuthorizationError,
                                    BadRequestError, NotFoundError)
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo, SortInfo
from imednet_sdk.models.study import StudyModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
STUDIES_ENDPOINT = "/api/v1/edc/studies"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def studies_client(client):
    """Fixture for StudiesClient."""
    return StudiesClient(client)


# --- Mock Data ---
MOCK_STUDY_1_DICT = {
    "sponsorKey": "100",
    "studyKey": "PHARMADEMO",
    "studyId": 100,
    "studyName": "iMednet Pharma Demonstration Study",
    "studyDescription": "iMednet Demonstration Study v2 Created 05April2018 After A5 Release",
    "studyType": "STUDY",
    "dateCreated": "2024-11-04 16:03:18",
    "dateModified": "2024-11-04 16:03:19",
}

MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",
    "path": STUDIES_ENDPOINT,
    "timestamp": "2024-11-04 16:03:18",
    "error": {},
}

MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "studyKey", "direction": "ASC"}],
}

MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_STUDY_1_DICT],
}


# --- Mock Error Data ---
MOCK_ERROR_METADATA_BASE = {
    "status": "ERROR",
    "method": "GET",
    "path": STUDIES_ENDPOINT,
    "timestamp": "2024-11-04 17:00:00",
}

MOCK_ERROR_BODY_400 = {
    "metadata": {
        **MOCK_ERROR_METADATA_BASE,
        "error": {
            "code": "1001",
            "message": "Invalid parameter value for 'size'. Must be between 1 and 500.",
            "details": "size parameter was -10",
        },
    },
    "pagination": None,
    "data": None,
}

MOCK_ERROR_BODY_401 = {
    "metadata": {
        **MOCK_ERROR_METADATA_BASE,
        "error": {
            "code": "AUTH-001",
            "message": "Authentication failed. Invalid API key or Security key.",
            "details": None,
        },
    },
    "pagination": None,
    "data": None,
}

MOCK_ERROR_BODY_403 = {
    "metadata": {
        **MOCK_ERROR_METADATA_BASE,
        "error": {
            "code": "AUTH-002",
            "message": "User does not have permission to access this resource.",
            "details": None,
        },
    },
    "pagination": None,
    "data": None,
}

MOCK_ERROR_BODY_404 = {
    "metadata": {
        **MOCK_ERROR_METADATA_BASE,
        "error": {
            "code": "API-404",
            "message": "Resource not found.",
            "details": f"Endpoint {STUDIES_ENDPOINT} not found",
        },
    },
    "pagination": None,
    "data": None,
}

MOCK_ERROR_BODY_500 = {
    "metadata": {
        **MOCK_ERROR_METADATA_BASE,
        "error": {
            "code": "SYS-500",
            "message": "An unexpected internal server error occurred.",
            "details": "Trace ID: xyz789",
        },
    },
    "pagination": None,
    "data": None,
}


# --- Test Cases ---
@respx.mock
def test_list_studies_success(studies_client, client):
    """Test successful retrieval of studies list."""
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = studies_client.list_studies()

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], StudyModel)
    assert response.data[0].studyKey == "PHARMADEMO"
    assert response.data[0].studyName == "iMednet Pharma Demonstration Study"
    assert (
        response.data[0].studyDescription
        == "iMednet Demonstration Study v2 Created 05April2018 After A5 Release"
    )
    assert response.data[0].studyType == "STUDY"
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:18")
    assert response.data[0].dateModified == datetime.fromisoformat("2024-11-04 16:03:19")

    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "studyKey"
    assert response.pagination.sort[0].direction == "ASC"


@respx.mock
def test_list_studies_with_params(studies_client, client):
    """Test retrieving studies list with pagination, sort, and filter."""
    params = {"page": 1, "size": 10, "sort": "studyKey,desc", "filter": "studyKey==PHARMADEMO"}

    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{STUDIES_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 1,
        "size": 10,
        "totalPages": 1,
        "totalElements": 0,
        "sort": [{"property": "studyKey", "direction": "DESC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }

    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}", params=params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = studies_client.list_studies(**params)

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "1"
    assert request.url.params["size"] == "10"
    assert request.url.params["sort"] == "studyKey,desc"
    assert request.url.params["filter"] == "studyKey==PHARMADEMO"

    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)
    assert response.pagination.currentPage == 1
    assert response.pagination.size == 10
    assert response.pagination.sort[0].property == "studyKey"
    assert response.pagination.sort[0].direction == "DESC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0


@respx.mock
def test_list_studies_empty_response(studies_client):
    """Test retrieving an empty list of studies."""
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{STUDIES_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 0,
        "size": 25,
        "totalPages": 0,
        "totalElements": 0,
        "sort": [{"property": "studyKey", "direction": "ASC"}],
    }
    empty_response_dict = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(200, json=empty_response_dict)
    )

    response = studies_client.list_studies()

    assert list_route.called
    assert response is not None
    assert isinstance(response.data, list)
    assert len(response.data) == 0
    assert isinstance(response.pagination, PaginationInfo)
    assert response.pagination.totalElements == 0
    assert response.pagination.totalPages == 0


@respx.mock
def test_list_studies_with_pagination(studies_client, client):
    """Test list_studies with pagination parameters."""
    expected_page = 2
    expected_size = 50
    expected_url_pattern = (
        f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}?page={expected_page}&size={expected_size}"
    )

    list_route = respx.get(url=expected_url_pattern).mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    studies_client.list_studies(page=expected_page, size=expected_size)

    assert list_route.called
    request = list_route.calls.last.request
    assert str(request.url) == expected_url_pattern


@respx.mock
def test_list_studies_with_sort(studies_client, client):
    """Test list_studies with sorting parameters."""
    sort_param = "studyName,desc"
    encoded_sort_param = urllib.parse.quote(sort_param)
    expected_url_pattern = f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}?sort={encoded_sort_param}"

    list_route = respx.get(url=expected_url_pattern).mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    studies_client.list_studies(sort=sort_param)

    assert list_route.called
    request = list_route.calls.last.request
    assert str(request.url) == expected_url_pattern


@respx.mock
def test_list_studies_with_filter(studies_client, client):
    """Test list_studies with filtering parameters."""
    filter_param = 'studyKey=="DEMO"'
    encoded_filter = urllib.parse.quote(filter_param)
    expected_url_pattern = f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}?filter={encoded_filter}"

    list_route = respx.get(url__regex=rf"{MOCK_BASE_URL}{STUDIES_ENDPOINT}\?filter=.*").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    studies_client.list_studies(filter=filter_param)

    assert list_route.called
    request = list_route.calls.last.request
    assert f"filter={encoded_filter}" in str(request.url)
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(str(request.url)).query)
    assert query_params.get("filter") == [filter_param]


@respx.mock
def test_list_studies_with_all_params(studies_client, client):
    """Test list_studies with all parameters combined."""
    page, size, sort, filter_str = 1, 100, "studyId,asc", 'studyType=="STUDY"'
    encoded_filter = urllib.parse.quote(filter_str)
    query_string = f"page={page}&size={size}&sort={sort}&filter={encoded_filter}"
    expected_url_pattern = f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}?{query_string}"

    list_route = respx.get(url__regex=rf"{MOCK_BASE_URL}{STUDIES_ENDPOINT}\?.*").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    studies_client.list_studies(page=page, size=size, sort=sort, filter=filter_str)

    assert list_route.called
    request = list_route.calls.last.request
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(str(request.url)).query)
    assert query_params.get("page") == [str(page)]
    assert query_params.get("size") == [str(size)]
    assert query_params.get("sort") == [sort]
    assert query_params.get("filter") == [filter_str]


# --- Error Handling Test Cases ---
@respx.mock
def test_list_studies_400_bad_request(studies_client):
    """Test list_studies raises BadRequestError on 400 response."""
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(400, json=MOCK_ERROR_BODY_400)
    )

    with pytest.raises(BadRequestError) as excinfo:
        studies_client.list_studies()

    assert list_route.called
    assert excinfo.value.status_code == 400
    assert excinfo.value.api_error_code == "1001"
    assert "Invalid parameter value" in excinfo.value.message
    assert excinfo.value.request_path == f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}"


@respx.mock
def test_list_studies_401_unauthorized(studies_client):
    """Test list_studies raises AuthenticationError on 401 response."""
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(401, json=MOCK_ERROR_BODY_401)
    )

    with pytest.raises(AuthenticationError) as excinfo:
        studies_client.list_studies()

    assert list_route.called
    assert excinfo.value.status_code == 401
    assert excinfo.value.api_error_code == "AUTH-001"
    assert "Authentication failed" in excinfo.value.message
    assert excinfo.value.request_path == f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}"


@respx.mock
def test_list_studies_403_forbidden(studies_client):
    """Test list_studies raises AuthorizationError on 403 response."""
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(403, json=MOCK_ERROR_BODY_403)
    )

    with pytest.raises(AuthorizationError) as excinfo:
        studies_client.list_studies()

    assert list_route.called
    assert excinfo.value.status_code == 403
    assert excinfo.value.api_error_code == "AUTH-002"
    assert "does not have permission" in excinfo.value.message
    assert excinfo.value.request_path == f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}"


@respx.mock
def test_list_studies_404_not_found(studies_client):
    """Test list_studies raises NotFoundError on 404 response."""
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(404, json=MOCK_ERROR_BODY_404)
    )

    with pytest.raises(NotFoundError) as excinfo:
        studies_client.list_studies()

    assert list_route.called
    assert excinfo.value.status_code == 404
    assert excinfo.value.api_error_code == "API-404"
    assert "Resource not found" in excinfo.value.message
    assert excinfo.value.request_path == f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}"
    assert not isinstance(excinfo.value, (BadRequestError, AuthenticationError, AuthorizationError))


@respx.mock
def test_list_studies_500_server_error(studies_client):
    """Test list_studies raises ApiError on 500 response."""
    list_route = respx.get(f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}").mock(
        return_value=Response(500, json=MOCK_ERROR_BODY_500)
    )

    with pytest.raises(ApiError) as excinfo:
        studies_client.list_studies()

    assert list_route.called
    assert excinfo.value.status_code == 500
    assert excinfo.value.api_error_code == "SYS-500"
    assert "internal server error" in excinfo.value.message.lower()
    assert excinfo.value.request_path == f"{MOCK_BASE_URL}{STUDIES_ENDPOINT}"
    assert not isinstance(excinfo.value, (BadRequestError, AuthenticationError, AuthorizationError))
