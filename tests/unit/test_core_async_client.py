import httpx
import pytest


@pytest.mark.asyncio
async def test_async_get_success(async_http_client, respx_mock_async_client, sample_data):
    respx_mock_async_client.get("/items").mock(return_value=httpx.Response(200, json=sample_data))

    response = await async_http_client.get("/items")

    assert response.status_code == 200
    assert response.json() == sample_data
