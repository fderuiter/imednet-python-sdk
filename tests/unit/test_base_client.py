from typing import Any
from unittest.mock import MagicMock

import httpx

import imednet.core.base_client as base_client
from imednet.constants import HEADER_API_KEY, HEADER_SECURITY_KEY
from imednet.core.base_client import BaseClient


class DummyClient(BaseClient):
    def _create_client(self, auth: Any) -> httpx.Client:
        headers = auth.get_headers()
        return httpx.Client(headers=headers)


def test_initialization_from_env(monkeypatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "env_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_secret")
    monkeypatch.setenv("IMEDNET_BASE_URL", "https://env.example.com")

    tracer = MagicMock()
    monkeypatch.setattr(base_client, "trace", MagicMock(get_tracer=lambda _: tracer))

    client = DummyClient()

    assert client.base_url == "https://env.example.com"
    assert client._client.headers[HEADER_API_KEY] == "env_key"
    assert client._client.headers[HEADER_SECURITY_KEY] == "env_secret"
    assert client._tracer is tracer
