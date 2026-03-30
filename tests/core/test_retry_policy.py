import httpx
import pytest

from imednet.core.client import Client
from imednet.core.retry import DefaultRetryPolicy, RetryState
from imednet.errors import ServerError


def test_default_policy_request_error():
    policy = DefaultRetryPolicy()
    state = RetryState(
        1, exception=httpx.RequestError("boom", request=httpx.Request("GET", "https://x"))
    )
    assert policy.should_retry(state)
    assert not policy.should_retry(RetryState(1))


def test_default_policy_retry_behavior():
    policy = DefaultRetryPolicy()

    # Retryable responses (Server Errors & Rate Limits)
    assert policy.should_retry(RetryState(1, result=httpx.Response(500)))
    assert policy.should_retry(RetryState(1, result=httpx.Response(502)))
    assert policy.should_retry(RetryState(1, result=httpx.Response(503)))
    assert policy.should_retry(RetryState(1, result=httpx.Response(504)))
    assert policy.should_retry(RetryState(1, result=httpx.Response(429)))

    # Non-retryable responses (Client Errors & Success)
    assert not policy.should_retry(RetryState(1, result=httpx.Response(400)))
    assert not policy.should_retry(RetryState(1, result=httpx.Response(401)))
    assert not policy.should_retry(RetryState(1, result=httpx.Response(403)))
    assert not policy.should_retry(RetryState(1, result=httpx.Response(404)))
    assert not policy.should_retry(RetryState(1, result=httpx.Response(200)))
    assert not policy.should_retry(RetryState(1, result=httpx.Response(201)))

    # Non-retryable exceptions
    assert not policy.should_retry(RetryState(1, exception=Exception("boom")))
    assert not policy.should_retry(RetryState(1, result=httpx.Response(200), exception=None))


def test_default_policy_non_request_exception(monkeypatch):
    client = Client("k", "s", base_url="https://api.test", retries=3)
    calls = {"count": 0}

    def request(method: str, url: str, **kwargs: object) -> httpx.Response:
        calls["count"] += 1
        raise RuntimeError("boom")

    monkeypatch.setattr(client._executor, "send", request)

    with pytest.raises(RuntimeError):
        client.get("/x")

    assert calls["count"] == 1


def test_custom_policy(monkeypatch):
    class ServerPolicy:
        def should_retry(self, state: RetryState) -> bool:
            return isinstance(state.exception, ServerError)

    client = Client("k", "s", base_url="https://api.test", retries=3, retry_policy=ServerPolicy())
    calls = {"count": 0}

    def request(method: str, url: str, **kwargs: object) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 3:
            raise ServerError({}, status_code=500)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(client._executor, "send", request)

    resp = client.get("/x")

    assert resp.status_code == 200
    assert calls["count"] == 3


def test_custom_policy_based_on_result(monkeypatch):
    class ResponsePolicy:
        def should_retry(self, state: RetryState) -> bool:
            resp = state.result
            return isinstance(resp, httpx.Response) and resp.status_code >= 500

    client = Client("k", "s", base_url="https://api.test", retries=3, retry_policy=ResponsePolicy())
    calls = {"count": 0}

    def request(method: str, url: str, **kwargs: object) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 3:
            return httpx.Response(500)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(client._executor, "send", request)

    resp = client.get("/x")

    assert resp.status_code == 200
    assert calls["count"] == 3
