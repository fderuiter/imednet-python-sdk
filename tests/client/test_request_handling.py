"""Tests for basic HTTP request handling (headers, methods, params)."""

import pytest
import respx
from httpx import Response

from .conftest import API_KEY, BASE_URL, SECURITY_KEY


@respx.mock
def test_get_request_headers_and_url(default_client):
    """Test GET request sends correct headers (x-api-key, x-imn-security-key, Accept)."""
    endpoint = "/studies"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json={"data": "success"}))

    response = default_client._get(endpoint)

    assert mock_route.called
    request = mock_route.calls.last.request
    assert str(request.url) == expected_url
    # Check all required headers
    assert request.headers["x-api-key"] == API_KEY
    assert request.headers["x-imn-security-key"] == SECURITY_KEY
    assert request.headers["accept"] == "application/json"
    assert response.status_code == 200
    assert response.json() == {"data": "success"}


@respx.mock
def test_post_request_headers_url_and_data(default_client):
    """Test POST request sends correct headers (incl Content-Type) and data."""
    endpoint = "/studies"
    expected_url = f"{BASE_URL}{endpoint}"
    payload = {"name": "New Study"}
    mock_route = respx.post(expected_url).mock(return_value=Response(201, json={"id": 1}))

    response = default_client._post(endpoint, json=payload)

    assert mock_route.called
    request = mock_route.calls.last.request
    assert str(request.url) == expected_url
    assert request.content == b'{"name":"New Study"}'
    # Check all required headers
    assert request.headers["x-api-key"] == API_KEY
    assert request.headers["x-imn-security-key"] == SECURITY_KEY
    assert request.headers["accept"] == "application/json"
    assert request.headers["content-type"] == "application/json"
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
