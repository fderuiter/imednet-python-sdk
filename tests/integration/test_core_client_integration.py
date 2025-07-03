import contextlib

import httpx
import pytest
import respx
from imednet.core import exceptions
from imednet.core.client import Client


@respx.mock
def test_successful_get_sync_client():
    client = Client("k", "s", base_url="https://api.test")
    respx.get("https://api.test/api/v1/edc/studies").respond(status_code=200, json={"data": [1]})

    resp = client.get("/api/v1/edc/studies")

    assert resp.status_code == 200
    assert resp.json() == {"data": [1]}


@respx.mock(assert_all_mocked=False)
def test_retry_on_transient_500(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client("k", "s", base_url="https://api.test", retries=3)
    calls = {"count": 0}

    def request(method: str, url: str, **kwargs: object) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 3:
            raise exceptions.ServerError({}, status_code=500)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(client._executor, "send", request)
    monkeypatch.setattr(
        client._executor,
        "should_retry",
        lambda state: isinstance(state.outcome.exception(), exceptions.ServerError),
    )

    resp = client.get("/api/v1/edc/studies")

    assert resp.status_code == 200
    assert calls["count"] == 3


@respx.mock
def test_authentication_error():
    client = Client("k", "s", base_url="https://api.test")
    respx.get("https://api.test/protected").respond(status_code=401, json={})

    with pytest.raises(exceptions.UnauthorizedError):
        client.get("/protected")


@respx.mock
def test_timeout_handling():
    client = Client("k", "s", base_url="https://api.test", timeout=1, retries=1)

    def slow(request):
        raise httpx.ReadTimeout("timeout", request=request)

    respx.get("https://api.test/slow").mock(side_effect=slow)

    with pytest.raises(httpx.ReadTimeout):
        client.get("/slow")


@respx.mock
def test_tracer_records_span():
    class DummyTracer:
        def __init__(self):
            self.called = False

        def start_as_current_span(self, name, attributes=None):
            self.called = True
            return contextlib.nullcontext()

    tracer = DummyTracer()
    client = Client("k", "s", base_url="https://api.test", tracer=tracer)
    respx.get("https://api.test/ping").respond(status_code=200, json={"ok": True})

    resp = client.get("/ping")

    assert resp.status_code == 200
    assert tracer.called
