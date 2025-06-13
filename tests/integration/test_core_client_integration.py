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


@respx.mock
def test_retry_on_transient_500():
    client = Client("k", "s", base_url="https://api.test", retries=3)
    call_count = {"n": 0}

    def responder(request):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise httpx.ReadTimeout("boom", request=request)
        return httpx.Response(200, json={"ok": True})

    respx.get("https://api.test/api/v1/edc/studies").mock(side_effect=responder)

    resp = client.get("/api/v1/edc/studies")

    assert resp.status_code == 200
    assert call_count["n"] == 3


@respx.mock
def test_authentication_error():
    client = Client("k", "s", base_url="https://api.test")
    respx.get("https://api.test/protected").respond(status_code=401, json={})

    with pytest.raises(exceptions.AuthenticationError):
        client.get("/protected")


@respx.mock
def test_timeout_handling():
    client = Client("k", "s", base_url="https://api.test", timeout=1, retries=1)

    def slow(request):
        raise httpx.ReadTimeout("timeout", request=request)

    respx.get("https://api.test/slow").mock(side_effect=slow)

    with pytest.raises(httpx.ReadTimeout):
        client.get("/slow")
