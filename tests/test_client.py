import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient  # Assuming client will be here

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


def test_request_timeout_custom(client):
    """Test that a custom timeout can be configured and is respected."""
    custom_timeout = 5.5
    timeout_client = ImednetClient(
        base_url=BASE_URL,
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        timeout=custom_timeout,
    )
    # The underlying httpx client should have the custom connect and read timeouts set
    assert timeout_client._client.timeout.connect == custom_timeout
    assert timeout_client._client.timeout.read == custom_timeout


@respx.mock
def test_retry_logic_on_failure(client):
    """Test that the client retries on specific error codes (e.g., 503)."""
    endpoint = "/retry-endpoint"
    expected_url = f"{BASE_URL}{endpoint}"
    # First return 503, then 200
    mock_route = respx.get(expected_url).mock(
        side_effect=[
            Response(503, json={"error": "server error"}),
            Response(200, json={"data": "success"}),
        ]
    )

    response = client._get(endpoint)

    # Ensure two calls were made: initial and retry
    assert mock_route.call_count == 2
    assert response.status_code == 200
    assert response.json() == {"data": "success"}
