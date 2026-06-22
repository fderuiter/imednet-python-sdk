"""TODO: Add docstring."""

from unittest.mock import MagicMock

import httpx
import pytest
import respx

from imednet import errors
from imednet.constants import DEFAULT_BASE_URL
from imednet.core.client import Client
from imednet.core.retry import RetryPolicy


def test_initialization_sets_defaults() -> None:
    """TODO: Add docstring."""
    client = Client(api_key="A", security_key="B")
    assert client.base_url == DEFAULT_BASE_URL
    assert client._client.headers["x-api-key"] == "A"
    assert client._client.headers["x-imn-security-key"] == "B"


def test_retry_logic_retries_request_errors() -> None:
    """TODO: Add docstring."""
    client = Client(api_key="A", security_key="B", base_url="https://api.test", retries=2)
    call_count = {"count": 0}

    def side_effect(request: httpx.Request) -> httpx.Response:
        """TODO: Add docstring."""
        call_count["count"] += 1
        if call_count["count"] == 1:
            raise httpx.RequestError("boom", request=request)
        return httpx.Response(200, json={"ok": True})

    with respx.mock(assert_all_called=True, assert_all_mocked=True) as respx_mock:
        respx_mock.get("https://api.test/path").mock(side_effect=side_effect)
        response = client.get("/path")

    assert call_count["count"] == 2
    assert response.json() == {"ok": True}


@pytest.mark.parametrize(
    "status,exc",
    [
        (400, errors.BadRequestError),
        (401, errors.UnauthorizedError),
        (403, errors.ForbiddenError),
        (404, errors.NotFoundError),
        (409, errors.ConflictError),
        (429, errors.RateLimitError),
        (500, errors.ServerError),
        (418, errors.ApiError),
    ],
)
def test_request_error_mapping(status, exc) -> None:
    """TODO: Add docstring."""
    client = Client(api_key="A", security_key="B", base_url="https://api.test")

    with respx.mock(assert_all_called=True, assert_all_mocked=True) as respx_mock:
        respx_mock.get("https://api.test/some").respond(status_code=status, json={"error": status})

        with pytest.raises(exc):
            client.get("/some")


def test_tracer_records_span() -> None:
    """TODO: Add docstring."""
    tracer = MagicMock()
    span_cm = MagicMock()
    span = MagicMock()
    span_cm.__enter__.return_value = span
    tracer.start_as_current_span.return_value = span_cm

    client = Client(api_key="A", security_key="B", base_url="https://api.test", tracer=tracer)

    with respx.mock(assert_all_called=True, assert_all_mocked=True) as respx_mock:
        respx_mock.get("https://api.test/trace").respond(status_code=200, json={"ok": True})
        client.get("/trace")

    tracer.start_as_current_span.assert_called_with(
        "http_request", attributes={"endpoint": "/trace", "method": "GET"}
    )
    span.set_attribute.assert_called_with("status_code", 200)


def test_base_url_sanitized() -> None:
    """TODO: Add docstring."""
    client = Client(api_key="A", security_key="B", base_url="https://host/api/")
    assert client.base_url == "https://host"


def test_retry_policy_accessor_updates_executor() -> None:
    """TODO: Add docstring."""
    client = Client(api_key="A", security_key="B")
    policy = MagicMock(spec=RetryPolicy)

    client.retry_policy = policy

    assert client.retry_policy is policy
    assert client._executor.retry_policy is policy
