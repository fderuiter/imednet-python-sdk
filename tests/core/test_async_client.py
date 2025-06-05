from unittest.mock import AsyncMock, Mock

import httpx
import pytest
import pytest_asyncio
from imednet.core.async_client import AsyncClient
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
from tenacity import RetryError


@pytest_asyncio.fixture
async def async_client():
    client = AsyncClient(api_key="test_api_key", security_key="test_security_key")
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_request_success(mocker, async_client):
    mock_response = Mock(spec=httpx.Response)
    mock_response.is_error = False
    mocker.patch.object(async_client._client, "request", AsyncMock(return_value=mock_response))

    response = await async_client._request("GET", "/test")

    assert response == mock_response


@pytest.mark.asyncio
async def test_request_retry_error(mocker):
    client = AsyncClient(api_key="test_api_key", security_key="test_security_key", retries=1)

    async def always_raise(*args, **kwargs):
        raise RetryError(None)

    mocker.patch("tenacity.AsyncRetrying.__call__", AsyncMock(side_effect=always_raise))

    with pytest.raises(RequestError):
        await client._request("GET", "/test")


@pytest.mark.asyncio
async def test_status_code_errors(mocker, async_client):
    cases = [
        (400, ValidationError),
        (401, AuthenticationError),
        (403, AuthorizationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (502, ServerError),
        (418, ApiError),
    ]
    for status, exc in cases:
        mock_response = Mock(spec=httpx.Response)
        mock_response.is_error = True
        mock_response.status_code = status
        mock_response.json.return_value = {"error": "boom"}
        mocker.patch.object(async_client._client, "request", AsyncMock(return_value=mock_response))

        with pytest.raises(exc):
            await async_client._request("GET", "/test")


@pytest.mark.asyncio
async def test_error_with_non_json_response(mocker, async_client):
    mock_response = Mock(spec=httpx.Response)
    mock_response.is_error = True
    mock_response.status_code = 500
    mock_response.json.side_effect = ValueError("bad json")
    mock_response.text = "Server Error"
    mocker.patch.object(async_client._client, "request", AsyncMock(return_value=mock_response))

    with pytest.raises(ServerError):
        await async_client._request("GET", "/test")
