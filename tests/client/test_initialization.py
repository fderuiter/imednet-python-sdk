"""Tests for client initialization and credential handling."""

import os

import pytest

from imednet_sdk.client import ImednetClient

from .conftest import API_KEY, BASE_URL, SECURITY_KEY


def test_client_initialization_explicit_keys(client_explicit_keys):
    """Test client initializes correctly with explicit keys."""
    assert client_explicit_keys.base_url == BASE_URL
    assert client_explicit_keys._api_key == API_KEY
    assert client_explicit_keys._security_key == SECURITY_KEY
    assert client_explicit_keys._client is not None
    assert client_explicit_keys._default_headers["x-api-key"] == API_KEY
    assert client_explicit_keys._default_headers["x-imn-security-key"] == SECURITY_KEY


def test_client_initialization_env_keys(client_env_keys):
    """Test client initializes correctly reading keys from environment variables."""
    assert client_env_keys.base_url == BASE_URL
    assert client_env_keys._api_key == API_KEY
    assert client_env_keys._security_key == SECURITY_KEY
    assert client_env_keys._client is not None
    assert client_env_keys._default_headers["x-api-key"] == API_KEY
    assert client_env_keys._default_headers["x-imn-security-key"] == SECURITY_KEY


def test_client_initialization_override_env_keys(client_override_env_keys):
    """Test client initialization uses explicit keys, overriding environment variables."""
    assert client_override_env_keys.base_url == BASE_URL
    # Should use the explicitly passed keys, not the env var keys
    assert client_override_env_keys._api_key == API_KEY
    assert client_override_env_keys._security_key == SECURITY_KEY
    assert client_override_env_keys._client is not None
    assert client_override_env_keys._default_headers["x-api-key"] == API_KEY
    assert client_override_env_keys._default_headers["x-imn-security-key"] == SECURITY_KEY


def test_client_initialization_missing_keys_error(client_no_keys):
    """Test ValueError is raised if keys are missing from args and environment."""
    with pytest.raises(ValueError, match="API key not provided"):
        client_no_keys()  # Attempt initialization without keys


def test_client_initialization_missing_api_key_error(monkeypatch):
    """Test ValueError is raised if only API key is missing."""
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", SECURITY_KEY)
    os.environ.pop("IMEDNET_API_KEY", None)
    with pytest.raises(ValueError, match="API key not provided"):
        ImednetClient(security_key=None)  # Pass None explicitly too


def test_client_initialization_missing_security_key_error(monkeypatch):
    """Test ValueError is raised if only Security key is missing."""
    monkeypatch.setenv("IMEDNET_API_KEY", API_KEY)
    os.environ.pop("IMEDNET_SECURITY_KEY", None)
    with pytest.raises(ValueError, match="Security key not provided"):
        ImednetClient(api_key=None)  # Pass None explicitly too
