import httpx

from imednet.core.retry import DefaultRetryPolicy, RetryState


def test_default_retry_policy_retries_on_network_errors():
    policy = DefaultRetryPolicy()

    # Simulate a network request error
    request = httpx.Request("GET", "https://example.com")
    error = httpx.RequestError("Network connection failed", request=request)
    state = RetryState(attempt_number=1, exception=error)

    assert policy.should_retry(state) is True


def test_default_retry_policy_retries_on_rate_limits():
    policy = DefaultRetryPolicy()

    # Simulate a 429 Too Many Requests response
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(429, request=request)
    state = RetryState(attempt_number=1, result=response)

    assert policy.should_retry(state) is True


def test_default_retry_policy_retries_on_server_errors():
    policy = DefaultRetryPolicy()

    # Simulate 500-599 Server Error responses
    request = httpx.Request("GET", "https://example.com")

    for status_code in [500, 502, 503, 504, 599]:
        response = httpx.Response(status_code, request=request)
        state = RetryState(attempt_number=1, result=response)
        assert policy.should_retry(state) is True


def test_default_retry_policy_does_not_retry_on_client_errors():
    policy = DefaultRetryPolicy()

    # Simulate 400-499 Client Error responses (excluding 429)
    request = httpx.Request("GET", "https://example.com")

    for status_code in [400, 401, 403, 404, 422]:
        response = httpx.Response(status_code, request=request)
        state = RetryState(attempt_number=1, result=response)
        assert policy.should_retry(state) is False


def test_default_retry_policy_does_not_retry_on_success():
    policy = DefaultRetryPolicy()

    # Simulate 200-299 Success responses
    request = httpx.Request("GET", "https://example.com")

    for status_code in [200, 201, 204]:
        response = httpx.Response(status_code, request=request)
        state = RetryState(attempt_number=1, result=response)
        assert policy.should_retry(state) is False


def test_default_retry_policy_does_not_retry_on_unrelated_exceptions():
    policy = DefaultRetryPolicy()

    # Simulate an exception that is not a RequestError
    error = ValueError("Something went wrong")
    state = RetryState(attempt_number=1, exception=error)

    assert policy.should_retry(state) is False


def test_default_retry_policy_with_no_result_or_exception():
    policy = DefaultRetryPolicy()

    # Simulate an empty state
    state = RetryState(attempt_number=1)

    assert policy.should_retry(state) is False
