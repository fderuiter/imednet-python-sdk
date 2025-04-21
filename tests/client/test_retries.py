"""Tests for client retry logic (default httpx and Tenacity)."""

import httpx
import pytest
import respx
from httpx import ConnectError, ReadTimeout, Response

from imednet_sdk.exceptions import ApiError, AuthenticationError, NotFoundError, RateLimitError

from .conftest import BASE_URL

# --- Default Retry Tests (based on httpx client config) --- #


@respx.mock
def test_retry_success_on_first_try(default_client):
    """Test successful request without any retries."""
    endpoint = "/success-first"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json={"data": "ok"}))

    response = default_client._get(endpoint)

    assert mock_route.call_count == 1
    assert response.status_code == 200
    assert response.json() == {"data": "ok"}


@respx.mock
def test_retry_on_configured_status(default_client):
    """Test retry happens for configured status codes (default 5xx)."""
    endpoint = "/retry-status"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(
        side_effect=[
            Response(503, json={"error": "service unavailable"}),
            Response(500, json={"error": "internal server error"}),
            Response(200, json={"data": "finally ok"}),
        ]
    )

    response = default_client._get(endpoint)  # Default retries = 3

    assert mock_route.call_count == 3  # Initial + 2 retries
    assert response.status_code == 200
    assert response.json() == {"data": "finally ok"}


@respx.mock
def test_retry_exceeds_attempts_status(default_client):
    """Test that the custom ApiError is raised after exceeding retries for 5xx."""
    endpoint = "/retry-fail-status"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(
        side_effect=[Response(503), Response(503), Response(503), Response(503)]
    )

    # Expect the custom ApiError after retries are exhausted
    with pytest.raises(ApiError) as exc_info:
        default_client._get(endpoint)  # Default retries = 3

    # Optionally, assert details about the caught exception
    assert exc_info.value.status_code == 503
    assert mock_route.call_count == 4  # Initial call + 3 retries


@respx.mock
def test_retry_on_request_error(default_client):
    """Test retry happens for ConnectError."""
    endpoint = "/retry-connect-error"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(
        side_effect=[
            ConnectError("Connection failed", request=None),
            Response(200, json={"data": "connected"}),
        ]
    )

    response = default_client._get(endpoint)  # Default retries = 3

    assert mock_route.call_count == 2  # Initial + 1 retry
    assert response.status_code == 200
    assert response.json() == {"data": "connected"}


@respx.mock
def test_retry_exceeds_attempts_request_error(default_client):
    """Test that the original RequestError is raised after exceeding retries."""
    endpoint = "/retry-fail-connect"
    expected_url = f"{BASE_URL}{endpoint}"
    original_exception = ConnectError("Connection failed repeatedly", request=None)
    mock_route = respx.get(expected_url).mock(
        side_effect=[original_exception] * 4  # Raise error 4 times
    )

    with pytest.raises(ConnectError) as exc_info:
        default_client._get(endpoint)  # Default retries = 3

    assert mock_route.call_count == 4  # Initial + 3 retries
    assert exc_info.value is original_exception  # Check it's the same exception instance


@respx.mock
def test_no_retry_on_4xx_error(default_client):
    """Test that retries do not happen for 4xx client errors and the correct custom exception is raised."""
    endpoint = "/no-retry-404"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(404))

    # Expect the custom NotFoundError
    with pytest.raises(NotFoundError) as exc_info:
        default_client._get(endpoint)

    # Assert that the request was made only once (no retries)
    assert mock_route.call_count == 1
    # Optionally, assert details about the caught exception
    assert exc_info.value.status_code == 404


# --- Tenacity Retry Logic Tests --- #


@respx.mock
def test_tenacity_retry_success_on_ratelimit_get(retry_client):
    """Test GET request retries on RateLimitError (429) and eventually succeeds."""
    endpoint = "/retry-ratelimit-get"
    expected_url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Rate limit exceeded"}}}
    success_payload = {"data": "ok after rate limit"}

    mock_route = respx.get(expected_url).mock(
        side_effect=[
            Response(429, json=error_payload),  # Attempt 1: RateLimitError
            Response(429, json=error_payload),  # Attempt 2: RateLimitError
            Response(200, json=success_payload),  # Attempt 3: Success
        ]
    )

    response = retry_client._get(endpoint)

    assert mock_route.call_count == 3
    assert response.status_code == 200
    assert response.json() == success_payload


@respx.mock
def test_tenacity_retry_success_on_apierror_get(retry_client):
    """Test GET request retries on ApiError (503) and eventually succeeds."""
    endpoint = "/retry-apierror-get"
    expected_url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Service Unavailable"}}}
    success_payload = {"data": "ok after server error"}

    mock_route = respx.get(expected_url).mock(
        side_effect=[
            Response(503, json=error_payload),  # Attempt 1: ApiError
            Response(500, json=error_payload),  # Attempt 2: ApiError
            Response(200, json=success_payload),  # Attempt 3: Success
        ]
    )

    response = retry_client._get(endpoint)

    assert mock_route.call_count == 3
    assert response.status_code == 200
    assert response.json() == success_payload


@respx.mock
def test_tenacity_retry_success_on_readtimeout_get(retry_client):
    """Test GET request retries on httpx.ReadTimeout and eventually succeeds."""
    endpoint = "/retry-timeout-get"
    expected_url = f"{BASE_URL}{endpoint}"
    success_payload = {"data": "ok after timeout"}

    mock_route = respx.get(expected_url).mock(
        side_effect=[
            httpx.ReadTimeout("Timeout during read", request=None),  # Attempt 1
            httpx.ReadTimeout("Timeout during read", request=None),  # Attempt 2
            Response(200, json=success_payload),  # Attempt 3: Success
        ]
    )

    response = retry_client._get(endpoint)

    assert mock_route.call_count == 3
    assert response.status_code == 200
    assert response.json() == success_payload


@respx.mock
def test_tenacity_retry_failure_on_ratelimit_get(retry_client):
    """Test GET request fails with RateLimitError after exhausting retries."""
    endpoint = "/retry-fail-ratelimit-get"
    expected_url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"code": "RL", "description": "Rate limit exceeded"}}}

    mock_route = respx.get(expected_url).mock(
        side_effect=[
            Response(429, json=error_payload),  # Attempt 1
            Response(429, json=error_payload),  # Attempt 2
            Response(429, json=error_payload),  # Attempt 3 (Final)
        ]
    )

    with pytest.raises(RateLimitError) as exc_info:
        retry_client._get(endpoint)

    assert mock_route.call_count == 3  # Initial + 2 retries
    exc = exc_info.value
    assert exc.status_code == 429
    assert exc.api_error_code == "RL"
    assert exc.message == "Rate limit exceeded"


@respx.mock
def test_tenacity_retry_failure_on_apierror_get(retry_client):
    """Test GET request fails with ApiError after exhausting retries."""
    endpoint = "/retry-fail-apierror-get"
    expected_url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"code": "5XX", "description": "Server Error"}}}

    mock_route = respx.get(expected_url).mock(
        side_effect=[
            Response(503, json=error_payload),  # Attempt 1
            Response(500, json=error_payload),  # Attempt 2
            Response(502, json=error_payload),  # Attempt 3 (Final)
        ]
    )

    with pytest.raises(ApiError) as exc_info:
        retry_client._get(endpoint)

    assert mock_route.call_count == 3  # Initial + 2 retries
    exc = exc_info.value
    assert exc.status_code == 502  # Should be the status of the *last* attempt
    assert exc.api_error_code == "5XX"
    assert exc.message == "Server Error"


@respx.mock
def test_tenacity_no_retry_on_ratelimit_post(retry_client):
    """Test POST request does NOT retry on RateLimitError (429) by default."""
    endpoint = "/no-retry-ratelimit-post"
    expected_url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Rate limit exceeded"}}}

    mock_route = respx.post(expected_url).mock(
        return_value=Response(429, json=error_payload)  # Only one response needed
    )

    with pytest.raises(RateLimitError) as exc_info:
        retry_client._post(endpoint, json={"data": "test"})

    assert mock_route.call_count == 1  # Should only be called once
    exc = exc_info.value
    assert exc.status_code == 429


@respx.mock
def test_tenacity_no_retry_on_authentication_error_get(retry_client):
    """Test GET request does NOT retry on AuthenticationError (401)."""
    endpoint = "/no-retry-auth-get"
    expected_url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"code": "9001", "description": "Invalid keys"}}}

    mock_route = respx.get(expected_url).mock(
        return_value=Response(401, json=error_payload)  # Only one response needed
    )

    with pytest.raises(AuthenticationError) as exc_info:
        retry_client._get(endpoint)

    assert mock_route.call_count == 1  # Should only be called once
    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.api_error_code == "9001"


@respx.mock
def test_tenacity_no_retry_on_notfound_error_get(retry_client):
    """Test GET request does NOT retry on NotFoundError (404)."""
    endpoint = "/no-retry-notfound-get"
    expected_url = f"{BASE_URL}{endpoint}"
    error_payload = {"metadata": {"error": {"description": "Not Found"}}}

    mock_route = respx.get(expected_url).mock(
        return_value=Response(404, json=error_payload)  # Only one response needed
    )

    with pytest.raises(NotFoundError) as exc_info:
        retry_client._get(endpoint)

    assert mock_route.call_count == 1  # Should only be called once
    exc = exc_info.value
    assert exc.status_code == 404
