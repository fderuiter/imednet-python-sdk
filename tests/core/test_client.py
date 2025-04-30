from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest
from imednet.core.client import Client
from imednet.core.exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
    ValidationError,
)


@pytest.fixture
def client():
    return Client(api_key="test_api_key", security_key="test_security_key")


class TestClient:
    def test_initialization(self):
        client = Client(api_key="test_api_key", security_key="test_security_key")

        assert client.base_url == Client.DEFAULT_BASE_URL
        assert client.retries == 3
        assert client.backoff_factor == 1.0
        assert isinstance(client.timeout, httpx.Timeout)
        assert client._client.headers["x-api-key"] == "test_api_key"
        assert client._client.headers["x-imn-security-key"] == "test_security_key"
        assert client._client.headers["Accept"] == "application/json"
        assert client._client.headers["Content-Type"] == "application/json"

    def test_custom_initialization(self):
        client = Client(
            api_key="test_api_key",
            security_key="test_security_key",
            base_url="https://custom.example.com",
            timeout=60.0,
            retries=5,
            backoff_factor=2.0,
        )

        assert client.base_url == "https://custom.example.com"
        assert client.retries == 5
        assert client.backoff_factor == 2.0
        assert client.timeout.read == 60.0

    def test_custom_timeout_object(self):
        # httpx.Timeout requires all four parameters if not using a default
        custom_timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0)
        client = Client(
            api_key="test_api_key", security_key="test_security_key", timeout=custom_timeout
        )
        assert client.timeout == custom_timeout

    def test_context_manager(self):
        with patch.object(Client, "close") as mock_close:
            with Client(api_key="test_api_key", security_key="test_security_key") as client:
                assert isinstance(client, Client)
            mock_close.assert_called_once()

    def test_close(self, client):
        with patch.object(client._client, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()

    def test_should_retry(self, client):
        # Should retry on httpx.RequestError
        mock_state = MagicMock()
        mock_state.outcome.exception.return_value = httpx.RequestError("Network error")
        assert client._should_retry(mock_state) is True

        # Should not retry on other exceptions
        mock_state.outcome.exception.return_value = ValueError("Other error")
        assert client._should_retry(mock_state) is False

        # Should not retry if outcome is None
        mock_state.outcome = None
        assert client._should_retry(mock_state) is False

    @patch("httpx.Client.request")
    def test_request_success(self, mock_request, client):
        mock_response = Mock(spec=httpx.Response)
        mock_response.is_error = False
        mock_request.return_value = mock_response

        response = client._request("GET", "/test")

        assert response == mock_response
        mock_request.assert_called_once_with("GET", "/test")

    @patch("httpx.Client.request")
    def test_request_retry_error(self, mock_request):
        # Use only 1 retry to speed up the test
        client = Client(api_key="test_api_key", security_key="test_security_key", retries=1)
        # Patch the retryer to always raise RetryError, simulating all retries failed
        from tenacity import RetryError

        class DummyRetryError(RetryError):
            def __init__(self, last_attempt):
                super().__init__(last_attempt)

        def always_raise(*args, **kwargs):
            raise DummyRetryError(None)

        import tenacity

        original_retrying_call = tenacity.Retrying.__call__
        tenacity.Retrying.__call__ = always_raise
        try:
            with pytest.raises(RequestError):
                client._request("GET", "/test")
        finally:
            tenacity.Retrying.__call__ = original_retrying_call

    @patch("httpx.Client.request")
    def test_status_code_errors(self, mock_request, client):
        error_cases = [
            (400, ValidationError),
            (401, AuthenticationError),
            (403, AuthorizationError),
            (404, NotFoundError),
            (429, RateLimitError),
            (500, ServerError),
            (502, ServerError),
            (418, ApiError),  # Any other error code
        ]

        for status_code, exception_class in error_cases:
            mock_response = Mock(spec=httpx.Response)
            mock_response.is_error = True
            mock_response.status_code = status_code
            mock_response.json.return_value = {"error": "test_error"}
            mock_request.return_value = mock_response

            with pytest.raises(exception_class):
                client._request("GET", "/test")

    @patch("httpx.Client.request")
    def test_error_with_non_json_response(self, mock_request, client):
        mock_response = Mock(spec=httpx.Response)
        mock_response.is_error = True
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Server Error"
        mock_request.return_value = mock_response

        with pytest.raises(ServerError):
            client._request("GET", "/test")

    @patch.object(Client, "_request")
    def test_get(self, mock_request, client):
        mock_response = Mock(spec=httpx.Response)
        mock_request.return_value = mock_response

        params = {"key": "value"}
        extra_kwarg = "extra_value"

        response = client.get("/test", params=params, extra_kwarg=extra_kwarg)

        assert response == mock_response
        mock_request.assert_called_once_with("GET", "/test", params=params, extra_kwarg=extra_kwarg)

    @patch.object(Client, "_request")
    def test_post(self, mock_request, client):
        mock_response = Mock(spec=httpx.Response)
        mock_request.return_value = mock_response

        json_data = {"data": "test"}
        extra_kwarg = "extra_value"

        response = client.post("/test", json=json_data, extra_kwarg=extra_kwarg)

        assert response == mock_response
        mock_request.assert_called_once_with(
            "POST", "/test", json=json_data, extra_kwarg=extra_kwarg
        )
