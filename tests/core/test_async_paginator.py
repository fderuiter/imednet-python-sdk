from unittest.mock import AsyncMock, MagicMock

import pytest
from imednet.core.async_paginator import AsyncPaginator


@pytest.mark.asyncio
async def test_iteration_single_page():
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"id": 1}, {"id": 2}],
        "pagination": {"totalPages": 1},
    }
    client.get = AsyncMock(return_value=mock_response)

    paginator = AsyncPaginator(client, "/api/test")
    results = [item async for item in paginator]

    assert results == [{"id": 1}, {"id": 2}]
    client.get.assert_called_once_with("/api/test", params={"page": 0, "size": 100})


@pytest.mark.asyncio
async def test_iteration_multiple_pages():
    client = MagicMock()
    responses = [
        {"data": [{"id": 1}, {"id": 2}], "pagination": {"totalPages": 2}},
        {"data": [{"id": 3}], "pagination": {"totalPages": 2}},
    ]
    client.get = AsyncMock(
        side_effect=[MagicMock(json=lambda: responses[0]), MagicMock(json=lambda: responses[1])]
    )

    paginator = AsyncPaginator(client, "/api/test")
    results = [item async for item in paginator]

    assert results == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert client.get.call_count == 2
