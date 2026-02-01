"""Tests for authentication strategy pattern."""

import os
from unittest.mock import patch

from imednet.auth.api_key import ApiKeyAuth
from imednet.core.client import Client


class MockAuthStrategy:
    def get_headers(self):
        return {"X-Custom-Auth": "secret"}


def test_api_key_auth_headers():
    auth = ApiKeyAuth(api_key="key", security_key="sec")
    headers = auth.get_headers()
    assert headers["x-api-key"] == "key"
    assert headers["x-imn-security-key"] == "sec"


def test_client_init_with_legacy_args():
    with patch("imednet.core.base_client.load_config") as mock_config:
        mock_config.return_value.api_key = "k"
        mock_config.return_value.security_key = "s"
        mock_config.return_value.base_url = "https://example.com"

        client = Client(api_key="k", security_key="s")
        assert isinstance(client.auth, ApiKeyAuth)
        assert client.auth.api_key == "k"
        assert client.auth.security_key == "s"
        assert client._client.headers["x-api-key"] == "k"
        assert client._client.headers["x-imn-security-key"] == "s"


def test_client_init_with_auth_strategy():
    auth = MockAuthStrategy()
    # We must provide base_url or have env var set because load_config is bypassed
    client = Client(auth=auth, base_url="https://auth.example.com")

    assert client.auth is auth
    assert client.base_url == "https://auth.example.com"
    assert client._client.headers["X-Custom-Auth"] == "secret"
    assert "x-api-key" not in client._client.headers


def test_client_init_with_auth_strategy_missing_base_url():
    auth = MockAuthStrategy()
    # Should fall back to DEFAULT_BASE_URL if no env var
    # We patch os.environ to ensure no env var
    with patch.dict(os.environ, {}, clear=True):
        from imednet.constants import DEFAULT_BASE_URL

        client = Client(auth=auth)
        assert client.base_url.rstrip("/") == DEFAULT_BASE_URL.rstrip("/")
