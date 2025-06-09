from __future__ import annotations

from typing import Any

import httpx
import pytest
from imednet.core.client import Client
from imednet.core.exceptions import NotFoundError


class DummyHttpxClient:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.request_args: tuple[str, str, dict[str, Any]] | None = None

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        self.request_args = (method, url, kwargs)
        return self.response

    def close(self) -> None:
        pass


def test_client_get_success(monkeypatch: pytest.MonkeyPatch) -> None:
    resp = httpx.Response(200, json={"ok": True})
    client = Client("k", "s", base_url="http://test")
    dummy = DummyHttpxClient(resp)
    monkeypatch.setattr(client, "_client", dummy)
    r = client.get("/foo")
    assert r.status_code == 200
    assert dummy.request_args[0] == "GET"


def test_client_request_raises_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    resp = httpx.Response(404, json={"error": "nope"})
    client = Client("k", "s", base_url="http://test")
    dummy = DummyHttpxClient(resp)
    monkeypatch.setattr(client, "_client", dummy)
    with pytest.raises(NotFoundError):
        client.get("/missing")
