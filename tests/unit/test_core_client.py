from unittest.mock import MagicMock

import httpx
import pytest

from imednet.constants import DEFAULT_BASE_URL
from imednet.core import exceptions
from imednet.core.base_client import BaseClient
from imednet.core.client import Client
from imednet.core.retry import RetryPolicy


class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
        self.request = httpx.Request("GET", "https://example.com")

    def json(self):
        return self._data

    @property
    def text(self):
        return str(self._data)

    @property
    def is_error(self):
        return self.status_code >= 400


def test_initialization_sets_defaults() -> None:
    client = Client(api_key="A", security_key="B")
    assert client.base_url == DEFAULT_BASE_URL
    assert client._client.headers["x-api-key"] == "A"
    assert client._client.headers["x-imn-security-key"] == "B"


def test_retry_logic_retries_request_errors(monkeypatch) -> None:
    client = Client(api_key="A", security_key="B", retries=2)
    call_count = {"count": 0}

    def side_effect(method: str, url: str, **kwargs):
        call_count["count"] += 1
        if call_count["count"] == 1:
            raise httpx.RequestError("boom", request=httpx.Request(method, url))
        return DummyResponse({"ok": True})

    monkeypatch.setattr(client._client, "request", side_effect)
    response = client.get("/path")
    assert call_count["count"] == 2
    assert response.json() == {"ok": True}


@pytest.mark.parametrize(
    "status,exc",
    [
        (400, exceptions.BadRequestError),
        (401, exceptions.UnauthorizedError),
        (403, exceptions.ForbiddenError),
        (404, exceptions.NotFoundError),
        (409, exceptions.ConflictError),
        (429, exceptions.RateLimitError),
        (500, exceptions.ServerError),
        (418, exceptions.ApiError),
    ],
)
def test_request_error_mapping(monkeypatch, status, exc) -> None:
    client = Client(api_key="A", security_key="B")
    resp = DummyResponse({"error": status}, status)
    monkeypatch.setattr(client._client, "request", lambda *a, **kw: resp)
    with pytest.raises(exc):
        client.get("/some")


def test_tracer_records_span(monkeypatch) -> None:
    tracer = MagicMock()
    span_cm = MagicMock()
    span = MagicMock()
    span_cm.__enter__.return_value = span
    tracer.start_as_current_span.return_value = span_cm

    client = Client(api_key="A", security_key="B", tracer=tracer)
    resp = DummyResponse({"ok": True}, 200)
    monkeypatch.setattr(client._client, "request", lambda *a, **kw: resp)

    client.get("/trace")

    tracer.start_as_current_span.assert_called_with(
        "http_request", attributes={"endpoint": "/trace", "method": "GET"}
    )
    span.set_attribute.assert_called_with("status_code", 200)


def test_base_url_sanitized() -> None:
    client = Client(api_key="A", security_key="B", base_url="https://host/api/")
    assert client.base_url == "https://host"


def test_retry_policy_accessor_updates_executor() -> None:
    client = Client(api_key="A", security_key="B")
    policy = MagicMock(spec=RetryPolicy)

    client.retry_policy = policy

    assert client.retry_policy is policy
    assert client._executor.retry_policy is policy
