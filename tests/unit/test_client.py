import httpx
import pytest

from imednet.core.client import Client
from imednet.core.exceptions import NotFoundError


class DummyHttpxClient:
    def __init__(self, response):
        self.response = response
        self.request_args = None

    def request(self, method, url, **kwargs):
        self.request_args = (method, url, kwargs)
        return self.response

    def close(self):
        pass


def test_client_get_success(monkeypatch):
    resp = httpx.Response(200, json={"ok": True})
    client = Client("k", "s", base_url="http://test")
    dummy = DummyHttpxClient(resp)
    monkeypatch.setattr(client, "_client", dummy)
    r = client.get("/foo")
    assert r.status_code == 200
    assert dummy.request_args[0] == "GET"


def test_client_request_raises_api_error(monkeypatch):
    resp = httpx.Response(404, json={"error": "nope"})
    client = Client("k", "s", base_url="http://test")
    dummy = DummyHttpxClient(resp)
    monkeypatch.setattr(client, "_client", dummy)
    with pytest.raises(NotFoundError):
        client.get("/missing")
