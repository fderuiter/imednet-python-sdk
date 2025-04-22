"""Tests for the Queries API client."""

from datetime import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.api.queries import QueriesClient  # Import specific client
from imednet_sdk.client import ImednetClient

# Use PaginationInfo based on _common.py
from imednet_sdk.models._common import ApiResponse, Metadata, PaginationInfo, SortInfo
from imednet_sdk.models.query import QueryCommentModel, QueryModel

# --- Constants ---
MOCK_BASE_URL = "https://testinstance.imednet.com"
MOCK_STUDY_KEY = "PHARMADEMO"  # Use example from docs
QUERIES_ENDPOINT = f"/api/v1/edc/studies/{MOCK_STUDY_KEY}/queries"


# --- Fixtures ---
@pytest.fixture
def client():
    """Fixture for ImednetClient."""
    return ImednetClient(
        api_key="test_api_key", security_key="test_security_key", base_url=MOCK_BASE_URL
    )


@pytest.fixture
def queries_client(client):
    """Fixture for QueriesClient."""
    return QueriesClient(client)


# --- Mock Data ---
# Corrected mock data based on docs/reference/queries.md example
MOCK_QUERY_COMMENT_1_DICT = {
    "sequence": 1,
    "annotationStatus": "Monitor Query Open",
    "user": "john",
    "comment": "Added comment to study",
    "closed": False,
    "date": "2024-11-04 16:03:19",
}

MOCK_QUERY_1_DICT = {
    "studyKey": MOCK_STUDY_KEY,
    "subjectId": 1,
    "subjectOid": "OID-1",
    "annotationType": "subject",
    "annotationId": 1,
    "type": None,  # As per docs example
    "description": "Monitor Query",
    "recordId": 123,
    "variable": "aeterm",
    "subjectKey": "123-005",
    "dateCreated": "2024-11-04 16:03:19",  # Use format from docs
    "dateModified": "2024-11-04 16:03:20",
    "queryComments": [MOCK_QUERY_COMMENT_1_DICT],
}
# MOCK_QUERY_2_DICT can be added if needed

# Corrected Metadata based on docs
MOCK_SUCCESS_METADATA_DICT = {
    "status": "OK",
    "method": "GET",  # Added method
    "path": QUERIES_ENDPOINT,
    "timestamp": "2024-11-04 16:03:19",  # Use fixed timestamp
    "error": {},
}

# Corrected Pagination based on docs
MOCK_PAGINATION_DICT = {
    "currentPage": 0,
    "size": 1,  # Adjusted to match single data item
    "totalPages": 1,
    "totalElements": 1,
    "sort": [{"property": "annotationId", "direction": "ASC"}],  # Use 'property'
}

# Corrected top-level response structure
MOCK_SUCCESS_RESPONSE_DICT = {
    "metadata": MOCK_SUCCESS_METADATA_DICT,
    "pagination": MOCK_PAGINATION_DICT,
    "data": [MOCK_QUERY_1_DICT],  # Use single item based on pagination
}


# --- Test Cases ---
@respx.mock
def test_list_queries_success(queries_client):
    """Test successful listing of queries."""
    list_route = respx.get(f"{MOCK_BASE_URL}{QUERIES_ENDPOINT}").mock(
        return_value=Response(200, json=MOCK_SUCCESS_RESPONSE_DICT)
    )

    response = queries_client.list_queries(study_key=MOCK_STUDY_KEY)

    assert list_route.called
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    # Assert pagination is present and correct type
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.metadata.status == "OK"
    assert response.metadata.path == QUERIES_ENDPOINT
    # Assert pagination fields based on documentation
    assert response.pagination.currentPage == 0
    assert response.pagination.size == 1
    assert response.pagination.totalPages == 1
    assert response.pagination.totalElements == 1
    assert isinstance(response.pagination.sort, list)
    assert len(response.pagination.sort) == 1
    assert isinstance(response.pagination.sort[0], SortInfo)
    assert response.pagination.sort[0].property == "annotationId"
    assert response.pagination.sort[0].direction == "ASC"

    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert isinstance(response.data[0], QueryModel)
    # Assertions based on corrected mock data
    assert response.data[0].annotationId == 1
    assert response.data[0].annotationType == "subject"
    assert response.data[0].description == "Monitor Query"
    assert response.data[0].subjectKey == "123-005"
    assert response.data[0].recordId == 123
    assert response.data[0].variable == "aeterm"
    assert response.data[0].dateCreated == datetime.fromisoformat("2024-11-04 16:03:19")
    assert response.data[0].dateModified == datetime.fromisoformat("2024-11-04 16:03:20")

    # Assert query comments
    assert isinstance(response.data[0].queryComments, list)
    assert len(response.data[0].queryComments) == 1
    assert isinstance(response.data[0].queryComments[0], QueryCommentModel)
    comment = response.data[0].queryComments[0]
    assert comment.sequence == 1
    assert comment.annotationStatus == "Monitor Query Open"
    assert comment.user == "john"
    assert comment.comment == "Added comment to study"
    assert comment.closed is False
    assert comment.date == datetime.fromisoformat("2024-11-04 16:03:19")


@respx.mock
def test_list_queries_with_params(queries_client):
    """Test listing queries with query parameters."""
    # Correct sort and filter syntax
    params = {"page": "2", "size": "5", "sort": "dateCreated,desc", "filter": "variable==aeterm"}
    # Mock response for this specific request (can be empty or tailored)
    mock_metadata = {**MOCK_SUCCESS_METADATA_DICT, "path": f"{QUERIES_ENDPOINT}"}
    mock_pagination = {
        "currentPage": 2,
        "size": 5,
        "totalPages": 3,
        "totalElements": 11,
        "sort": [{"property": "dateCreated", "direction": "DESC"}],
    }
    mock_response = {
        "metadata": mock_metadata,
        "pagination": mock_pagination,
        "data": [],
    }  # Example empty data

    list_route = respx.get(f"{MOCK_BASE_URL}{QUERIES_ENDPOINT}", params=params).mock(
        return_value=Response(200, json=mock_response)
    )

    response = queries_client.list_queries(
        study_key=MOCK_STUDY_KEY, page=2, size=5, sort="dateCreated,desc", filter="variable==aeterm"
    )

    assert list_route.called
    request = list_route.calls.last.request
    assert request.url.params["page"] == "2"
    assert request.url.params["size"] == "5"
    assert request.url.params["sort"] == "dateCreated,desc"
    assert request.url.params["filter"] == "variable==aeterm"

    # Assert response structure
    assert isinstance(response, ApiResponse)
    assert isinstance(response.metadata, Metadata)
    assert isinstance(response.pagination, PaginationInfo)  # Check for PaginationInfo type
    assert response.pagination.currentPage == 2
    assert response.pagination.size == 5
    assert response.pagination.sort[0].property == "dateCreated"
    assert response.pagination.sort[0].direction == "DESC"
    assert isinstance(response.data, list)
    assert len(response.data) == 0  # Based on mock response


def test_list_queries_missing_study_key(queries_client):
    """Test listing queries with missing study_key raises ValueError."""
    # Match error message from client implementation
    with pytest.raises(ValueError, match="study_key cannot be empty"):
        queries_client.list_queries(study_key="")

    with pytest.raises(ValueError, match="study_key cannot be empty"):
        queries_client.list_queries(study_key=None)  # type: ignore
