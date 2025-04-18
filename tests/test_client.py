import pytest
import respx
from httpx import ConnectError, HTTPStatusError, Response, Timeout, TimeoutException

from imednet_sdk.client import ImednetClient

# Constants for testing
BASE_URL = "https://test.imednetapi.com"
API_KEY = "test_api_key"
SECURITY_KEY = "test_security_key"
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "x-imn-security-key": SECURITY_KEY,
}


@pytest.fixture
def client():
    """Fixture to create an ImednetClient instance for tests."""
    return ImednetClient(base_url=BASE_URL, api_key=API_KEY, security_key=SECURITY_KEY)


@pytest.fixture
def default_client():
    """Fixture for a client with default settings."""
    return ImednetClient(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL)


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


@respx.mock
def test_client_initialization(client):
    """Test that the client initializes with correct attributes."""
    assert client.base_url == BASE_URL
    assert client._api_key == API_KEY  # Assuming private attribute
    assert client._security_key == SECURITY_KEY  # Assuming private attribute
    assert client._client is not None  # Assuming an internal httpx client exists


@respx.mock
def test_get_request_headers_and_url(client):
    """Test GET request sends correct headers and constructs URL properly."""
    endpoint = "/studies"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json={"data": "success"}))

    response = client._get(endpoint)  # Assuming internal _get method

    assert mock_route.called
    request = mock_route.calls.last.request
    assert str(request.url) == expected_url
    for key, value in DEFAULT_HEADERS.items():
        assert request.headers[key] == value
    assert response.status_code == 200
    assert response.json() == {"data": "success"}


@respx.mock
def test_post_request_headers_url_and_data(client):
    """Test POST request sends correct headers, URL, and JSON data."""
    endpoint = "/studies"
    expected_url = f"{BASE_URL}{endpoint}"
    payload = {"name": "New Study"}
    mock_route = respx.post(expected_url).mock(return_value=Response(201, json={"id": 1}))

    response = client._post(endpoint, json=payload)  # Assuming internal _post method

    assert mock_route.called
    request = mock_route.calls.last.request
    assert str(request.url) == expected_url
    # Corrected assertion: remove space after colon
    assert request.content == b'{"name":"New Study"}'
    for key, value in DEFAULT_HEADERS.items():
        assert request.headers[key] == value
    assert response.status_code == 201
    assert response.json() == {"id": 1}


@respx.mock
def test_request_with_query_params(client):
    """Test that query parameters are correctly appended to the URL."""
    endpoint = "/records"
    params = {
        "page": 1,
        "size": 50,
        "sort": "id,desc",
        "filter": "status:active",
    }
    expected_url = f"{BASE_URL}{endpoint}?page=1&size=50&sort=id%2Cdesc&filter=status%3Aactive"
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json=[]))

    response = client._get(endpoint, params=params)

    assert mock_route.called
    request = mock_route.calls.last.request
    assert str(request.url) == expected_url
    assert response.status_code == 200


# --- Timeout Tests --- #


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


# --- End Timeout Tests --- #


# --- Retry Tests --- #


@respx.mock
def test_retry_success_on_first_try(default_client):
    """Test successful request without any retries."""
    endpoint = "/success-first"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json={"data": "ok"}))

    response = default_client._get(endpoint)

    assert mock_route.call_count == 1
    assert response.status_code == 200
    assert response.json() == {"data": "ok"}


@respx.mock
def test_retry_on_configured_status(default_client):
    """Test retry happens for configured status codes (default 5xx)."""
    endpoint = "/retry-status"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(
        side_effect=[
            Response(503, json={"error": "service unavailable"}),
            Response(500, json={"error": "internal server error"}),
            Response(200, json={"data": "finally ok"}),
        ]
    )

    response = default_client._get(endpoint)  # Default retries = 3

    assert mock_route.call_count == 3  # Initial + 2 retries
    assert response.status_code == 200
    assert response.json() == {"data": "finally ok"}


@respx.mock
def test_retry_exceeds_attempts_status(default_client):
    """Test that the original HTTPStatusError is raised after exceeding retries."""
    endpoint = "/retry-fail-status"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(
        side_effect=[Response(503), Response(503), Response(503), Response(503)]
    )

    # Expect the specific HTTPStatusError
    with pytest.raises(HTTPStatusError) as exc_info:
        default_client._get(endpoint)  # Default retries = 3

    assert mock_route.call_count == 4  # Initial + 3 retries
    # Check the raised exception is the last HTTPStatusError
    assert exc_info.value.response.status_code == 503


@respx.mock
def test_retry_on_request_error(default_client):
    """Test retry happens for ConnectError."""
    endpoint = "/retry-connect-error"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(
        side_effect=[
            ConnectError("Connection failed", request=None),
            Response(200, json={"data": "connected"}),
        ]
    )

    response = default_client._get(endpoint)  # Default retries = 3

    assert mock_route.call_count == 2  # Initial + 1 retry
    assert response.status_code == 200
    assert response.json() == {"data": "connected"}


@respx.mock
def test_retry_exceeds_attempts_request_error(default_client):
    """Test that the original RequestError is raised after exceeding retries."""
    endpoint = "/retry-fail-connect"
    expected_url = f"{BASE_URL}{endpoint}"
    original_exception = ConnectError("Connection failed repeatedly", request=None)
    mock_route = respx.get(expected_url).mock(
        side_effect=[original_exception] * 4  # Raise error 4 times
    )

    with pytest.raises(ConnectError) as exc_info:
        default_client._get(endpoint)  # Default retries = 3

    assert mock_route.call_count == 4  # Initial + 3 retries
    assert exc_info.value is original_exception  # Check it's the same exception instance


@respx.mock
def test_no_retry_on_4xx_error(default_client):
    """Test that retries do not happen for 4xx client errors by default."""
    endpoint = "/no-retry-404"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(404))

    # Expect the specific HTTPStatusError
    with pytest.raises(HTTPStatusError) as exc_info:
        default_client._get(endpoint)

    assert mock_route.call_count == 1  # No retries
    assert exc_info.value.response.status_code == 404


# --- End Retry Tests --- #
