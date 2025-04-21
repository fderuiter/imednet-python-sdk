"""Shared fixtures for client tests."""

import os
from datetime import datetime
from typing import List, Optional

import pytest
from httpx import Timeout
from pydantic import BaseModel, Field

from imednet_sdk.client import ImednetClient

# --- Constants --- #

BASE_URL = "https://test.imednetapi.com"
API_KEY = "test_api_key"
SECURITY_KEY = "test_security_key"
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "x-imn-security-key": SECURITY_KEY,
}

# --- Simple Pydantic Model for Testing --- #


class SimpleTestModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = Field(..., alias="isActive")


# --- Client Fixtures --- #


@pytest.fixture
def client():
    """Fixture to create an ImednetClient instance for tests."""
    return ImednetClient(base_url=BASE_URL, api_key=API_KEY, security_key=SECURITY_KEY)


@pytest.fixture
def client_explicit_keys():
    """Fixture for a client with explicitly passed keys."""
    return ImednetClient(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL)


@pytest.fixture
def client_no_keys():
    """Fixture attempting client init with no keys provided or in env."""
    # Ensure env vars are unset for this test
    os.environ.pop("IMEDNET_API_KEY", None)
    os.environ.pop("IMEDNET_SECURITY_KEY", None)
    return ImednetClient  # Return the class itself to test __init__ raising error


@pytest.fixture
def client_env_keys(monkeypatch):
    """Fixture for a client reading keys from environment variables."""
    monkeypatch.setenv("IMEDNET_API_KEY", API_KEY)
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", SECURITY_KEY)
    # Don't pass keys to init
    return ImednetClient(base_url=BASE_URL)


@pytest.fixture
def client_override_env_keys(monkeypatch):
    """Fixture for a client where explicit keys override env vars."""
    monkeypatch.setenv("IMEDNET_API_KEY", "env_api_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_security_key")
    # Pass different keys explicitly
    return ImednetClient(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL)


@pytest.fixture
def default_client(client_explicit_keys):
    """Fixture for a client with default settings (using explicit keys)."""
    return client_explicit_keys


@pytest.fixture
def custom_timeout_client():
    """Fixture for a client with a custom float timeout."""
    return ImednetClient(
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        base_url=BASE_URL,
        timeout=5.5,
    )


@pytest.fixture
def custom_timeout_object_client():
    """Fixture for a client with a custom Timeout object."""
    return ImednetClient(
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        base_url=BASE_URL,
        timeout=Timeout(10.0, connect=2.0),
    )


@pytest.fixture
def retry_client():
    """Client configured with 2 retries (3 total attempts)."""
    return ImednetClient(
        base_url=BASE_URL,
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        retries=2,  # Initial + 2 retries = 3 attempts
        backoff_factor=0.1,  # Use a small backoff for faster tests
    )
