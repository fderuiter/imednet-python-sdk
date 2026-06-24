"""TODO: Add docstring."""

import httpx
import pytest

from imednet.core.retry import DefaultRetryPolicy, RetryState


def test_default_retry_policy_retries_on_network_errors():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Simulate a network request error for an idempotent method (GET)
    request = httpx.Request("GET", "https://example.com")
    error = httpx.RequestError("Network connection failed", request=request)
    state = RetryState(attempt_number=1, exception=error, method="GET")

    assert policy.should_retry(state) is True


def test_default_retry_policy_retries_on_rate_limits():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Simulate a 429 Too Many Requests response — retried regardless of method
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(429, request=request)
    state = RetryState(attempt_number=1, result=response)

    assert policy.should_retry(state) is True


def test_default_retry_policy_retries_on_server_errors():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Simulate 500-599 Server Error responses for an idempotent method (GET)
    request = httpx.Request("GET", "https://example.com")

    for status_code in [500, 502, 503, 504, 599]:
        response = httpx.Response(status_code, request=request)
        state = RetryState(attempt_number=1, result=response, method="GET")
        assert policy.should_retry(state) is True


def test_default_retry_policy_does_not_retry_on_client_errors():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Simulate 400-499 Client Error responses (excluding 429)
    request = httpx.Request("GET", "https://example.com")

    for status_code in [400, 401, 403, 404, 422]:
        response = httpx.Response(status_code, request=request)
        state = RetryState(attempt_number=1, result=response, method="GET")
        assert policy.should_retry(state) is False


def test_default_retry_policy_does_not_retry_on_success():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Simulate 200-299 Success responses
    request = httpx.Request("GET", "https://example.com")

    for status_code in [200, 201, 204]:
        response = httpx.Response(status_code, request=request)
        state = RetryState(attempt_number=1, result=response, method="GET")
        assert policy.should_retry(state) is False


def test_default_retry_policy_does_not_retry_on_unrelated_exceptions():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Simulate an exception that is not a RequestError
    error = ValueError("Something went wrong")
    state = RetryState(attempt_number=1, exception=error, method="GET")

    assert policy.should_retry(state) is False


def test_default_retry_policy_with_no_result_or_exception():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Simulate an empty state
    state = RetryState(attempt_number=1)

    assert policy.should_retry(state) is False


@pytest.mark.parametrize("method", ["POST", "PATCH"])
def test_default_retry_policy_does_not_retry_non_idempotent_on_network_error(
    method: str,
):
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    request = httpx.Request(method, "https://example.com")
    error = httpx.ConnectError("Connection failed", request=request)
    state = RetryState(attempt_number=1, exception=error, method=method)

    # Non-idempotent methods must never be retried on network errors
    assert policy.should_retry(state) is False


@pytest.mark.parametrize("method", ["POST", "PATCH"])
def test_default_retry_policy_does_not_retry_non_idempotent_on_server_error(
    method: str,
):
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    request = httpx.Request(method, "https://example.com")
    response = httpx.Response(503, request=request)
    state = RetryState(attempt_number=1, result=response, method=method)

    # Non-idempotent methods must never be retried on 5xx responses
    assert policy.should_retry(state) is False


def test_default_retry_policy_retries_post_on_rate_limit():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # 429 means the server rejected the request before processing it, so
    # retrying a POST is safe even under the default policy.
    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(429, request=request)
    state = RetryState(attempt_number=1, result=response, method="POST")

    assert policy.should_retry(state) is True


def test_default_retry_policy_does_not_retry_unknown_method_on_network_error():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Unknown / missing method → fail-safe: do not retry
    request = httpx.Request("GET", "https://example.com")
    error = httpx.RequestError("timeout", request=request)
    state = RetryState(attempt_number=1, exception=error, method=None)

    assert policy.should_retry(state) is False


def test_default_retry_policy_does_not_retry_unknown_method_on_server_error():
    """TODO: Add docstring."""
    policy = DefaultRetryPolicy()

    # Unknown / missing method → fail-safe: do not retry
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(500, request=request)
    state = RetryState(attempt_number=1, result=response, method=None)

    assert policy.should_retry(state) is False
