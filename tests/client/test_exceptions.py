"""Tests for custom exception mapping based on API responses."""

# Note: These tests were copied from the original test_client.py
# They rely on the _handle_error method which might be implicitly tested elsewhere,
# but keeping them separate focuses on the exception mapping logic.

import pytest
import respx
from httpx import Response

from imednet_sdk.exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

from .conftest import BASE_URL

# --- Custom Exception Mapping Tests --- #


@respx.mock
def test_raises_validation_error_400_code_1000(default_client):
    """Test 400 response with code 1000 raises ValidationError."""
    endpoint = "/error-400-1000"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"code": "1000", "description": "Validation failed"}}}
    respx.get(url).mock(return_value=Response(400, json=error_payload))

    with pytest.raises(ValidationError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 400
    assert exc.api_error_code == "1000"
    assert exc.message == "Validation failed"


@respx.mock
def test_raises_bad_request_error_400_other_code(default_client):
    """Test 400 response with other code raises BadRequestError."""
    endpoint = "/error-400-other"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"code": "1001", "description": "Bad request"}}}
    respx.get(url).mock(return_value=Response(400, json=error_payload))

    with pytest.raises(BadRequestError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 400
    assert exc.api_error_code == "1001"
    assert exc.message == "Bad request"


@respx.mock
def test_raises_bad_request_error_400_no_code(default_client):
    """Test 400 response with no code raises BadRequestError."""
    endpoint = "/error-400-no-code"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Missing parameter"}}}
    respx.get(url).mock(return_value=Response(400, json=error_payload))

    with pytest.raises(BadRequestError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 400
    assert exc.api_error_code is None
    assert exc.message == "Missing parameter"


@respx.mock
def test_raises_authentication_error_401_code_9001(default_client):
    """Test 401 response with code 9001 raises AuthenticationError."""
    endpoint = "/error-401-9001"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"code": "9001", "description": "Invalid API key"}}}
    respx.get(url).mock(return_value=Response(401, json=error_payload))

    with pytest.raises(AuthenticationError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.api_error_code == "9001"
    assert exc.message == "Invalid API key"


@respx.mock
def test_raises_authentication_error_401_other(default_client):
    """Test 401 response with other/no code raises AuthenticationError."""
    endpoint = "/error-401-other"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Authentication required"}}}
    respx.get(url).mock(return_value=Response(401, json=error_payload))

    with pytest.raises(AuthenticationError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.api_error_code is None
    assert exc.message == "Authentication required"


@respx.mock
def test_raises_authorization_error_403(default_client):
    """Test 403 response raises AuthorizationError."""
    endpoint = "/error-403"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Forbidden"}}}
    respx.get(url).mock(return_value=Response(403, json=error_payload))

    with pytest.raises(AuthorizationError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 403
    assert exc.api_error_code is None
    assert exc.message == "Forbidden"


@respx.mock
def test_raises_not_found_error_404(default_client):
    """Test 404 response raises NotFoundError."""
    endpoint = "/error-404"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Resource not found"}}}
    respx.get(url).mock(return_value=Response(404, json=error_payload))

    with pytest.raises(NotFoundError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 404
    assert exc.api_error_code is None
    assert exc.message == "Resource not found"


@respx.mock
def test_raises_rate_limit_error_429(default_client):
    """Test 429 response raises RateLimitError."""
    endpoint = "/error-429"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Too many requests"}}}
    respx.get(url).mock(return_value=Response(429, json=error_payload))

    with pytest.raises(RateLimitError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 429
    assert exc.api_error_code is None
    assert exc.message == "Too many requests"


@respx.mock
def test_raises_api_error_500_code_9000(default_client):
    """Test 500 response with code 9000 raises ApiError."""
    endpoint = "/error-500-9000"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {
        "metadata": {"error": {"code": "9000", "description": "Internal server error"}}
    }
    respx.get(url).mock(return_value=Response(500, json=error_payload))

    with pytest.raises(ApiError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 500
    assert exc.api_error_code == "9000"
    assert exc.message == "Internal server error"


@respx.mock
def test_raises_api_error_500_other(default_client):
    """Test 500 response with other/no code raises ApiError."""
    endpoint = "/error-500-other"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Something went wrong"}}}
    respx.get(url).mock(return_value=Response(500, json=error_payload))

    with pytest.raises(ApiError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 500
    assert exc.api_error_code is None
    assert exc.message == "Something went wrong"


@respx.mock
def test_raises_api_error_503(default_client):
    """Test 503 response raises ApiError."""
    endpoint = "/error-503"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Service unavailable"}}}
    respx.get(url).mock(return_value=Response(503, json=error_payload))

    with pytest.raises(ApiError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 503
    assert exc.api_error_code is None
    assert exc.message == "Service unavailable"


@respx.mock
def test_raises_api_error_other_4xx(default_client):
    """Test other 4xx response (e.g., 418) raises ApiError."""
    endpoint = "/error-418"
    url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "I'm a teapot"}}}
    respx.get(url).mock(return_value=Response(418, json=error_payload))

    with pytest.raises(ApiError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 418
    assert exc.api_error_code is None
    assert exc.message == "I'm a teapot"


@respx.mock
def test_handle_error_non_json_response(default_client):
    """Test that ApiError is raised for non-JSON error responses."""
    endpoint = "/error-non-json"
    url = f"{BASE_URL}{endpoint}"
    respx.get(url).mock(return_value=Response(500, text="Internal Server Error Text"))

    with pytest.raises(ApiError) as exc_info:
        default_client._get(endpoint)

    exc = exc_info.value
    assert exc.status_code == 500
    assert exc.api_error_code is None
    # Check the updated error message format - it no longer includes the raw text
    assert "HTTP error 500 occurred" in exc.message
