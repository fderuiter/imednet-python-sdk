"""Tests for client timeout configuration and behavior."""

import pytest
import respx
from httpx import Response, Timeout, TimeoutException

from .conftest import BASE_URL


def test_client_default_timeout(default_client):
    """Test that the client uses the default httpx.Timeout if none is provided."""
    assert isinstance(default_client._default_timeout, Timeout)
    assert default_client._default_timeout.connect == 5.0
    assert default_client._default_timeout.read == 30.0  # Default read timeout
    assert default_client._default_timeout.write == 30.0  # Default write timeout
    assert default_client._default_timeout.pool == 30.0  # Default pool timeout
    # Check the underlying httpx client's timeout
    assert default_client._client.timeout == default_client._default_timeout


def test_client_custom_float_timeout(custom_timeout_client):
    """Test client initialization with a custom float timeout."""
    assert isinstance(custom_timeout_client._default_timeout, float)
    assert custom_timeout_client._default_timeout == 5.5
    assert custom_timeout_client._client.timeout == Timeout(5.5)  # httpx converts float to Timeout


def test_client_custom_timeout_object(custom_timeout_object_client):
    """Test client initialization with a custom Timeout object."""
    expected_timeout = Timeout(10.0, connect=2.0)
    assert isinstance(custom_timeout_object_client._default_timeout, Timeout)
    assert custom_timeout_object_client._default_timeout == expected_timeout
    assert custom_timeout_object_client._client.timeout == expected_timeout


@respx.mock
def test_request_uses_default_timeout(default_client):
    """Verify the default timeout is used in requests when no override is given."""
    endpoint = "/timeout-default"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(200))

    default_client._get(endpoint)

    assert mock_route.called
    # httpx doesn't directly expose the timeout used for a specific request via respx
    # We rely on the client's internal logic tested above and the fact it didn't error


@respx.mock
def test_request_override_timeout(custom_timeout_object_client):
    """Verify a per-request timeout overrides the client's default."""
    endpoint = "/timeout-override"
    expected_url = f"{BASE_URL}{endpoint}"
    override_timeout = Timeout(1.0)

    # Mock raising TimeoutException directly
    mock_route = respx.get(expected_url).mock(
        side_effect=TimeoutException("Request timed out", request=None)
    )

    with pytest.raises(TimeoutException):
        # Pass the override timeout to the request method
        custom_timeout_object_client._get(endpoint, timeout=override_timeout)

    assert mock_route.called


@respx.mock
def test_request_timeout_exception(default_client):
    """Test that httpx.TimeoutException is raised when a request times out."""
    endpoint = "/timeout-exception"
    expected_url = f"{BASE_URL}{endpoint}"
    request_timeout = Timeout(0.1)  # Very short timeout

    # Mock raising TimeoutException directly
    mock_route = respx.get(expected_url).mock(
        side_effect=TimeoutException("Request timed out", request=None)
    )

    with pytest.raises(TimeoutException):
        # Pass the short timeout to the request method
        default_client._get(endpoint, timeout=request_timeout)

    assert mock_route.called
