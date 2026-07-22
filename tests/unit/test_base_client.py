"""Unit tests for base client."""

from unittest.mock import MagicMock

import httpx

from imednet.auth.strategy import AuthStrategy
from imednet.constants import HEADER_API_KEY, HEADER_SECURITY_KEY
from imednet.core import base_client
from imednet.core.base_client import BaseClient


class DummyClient(BaseClient):
    """Test suite for DummyClient."""

    def _create_client(self, auth: AuthStrategy) -> httpx.Client:
        """Helper function to  create client."""
        headers = auth.get_headers()
        return httpx.Client(headers=headers)


def test_initialization_from_env(monkeypatch) -> None:
    """Test that initialization from env."""
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
