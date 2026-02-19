from typing import Any, Dict, List

import pytest

from imednet.core.paginator import (
    AsyncJsonListPaginator,
    AsyncPaginator,
    JsonListPaginator,
    Paginator,
)


class DummyClient:
    def __init__(self, responses: List[Dict[str, Any]]):
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []

    def get(self, path: str, params: Dict[str, Any] | None = None):
        self.calls.append({"path": path, "params": params})
        data = self.responses.pop(0)
        return type("Resp", (), {"json": lambda self: data})()


class AsyncDummyClient:
    def __init__(self, responses: List[Dict[str, Any]]):
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []

    async def get(self, path: str, params: Dict[str, Any] | None = None):
        self.calls.append({"path": path, "params": params})
        data = self.responses.pop(0)
        return type("Resp", (), {"json": lambda self: data})()


def test_single_page_iteration() -> None:
    client = DummyClient([{"data": [1, 2]}])
    paginator = Paginator(client, "/p")
    assert list(paginator) == [1, 2]
    assert client.calls[0]["params"]["page"] == 0


def test_multiple_page_iteration() -> None:
    client = DummyClient(
        [
            {"data": [1], "pagination": {"totalPages": 2}},
            {"data": [2], "pagination": {"totalPages": 2}},
        ]
    )
    paginator = Paginator(client, "/p", params={"a": 1}, page_size=10)
    items = list(paginator)
    assert items == [1, 2]
    assert client.calls[0]["params"] == {"a": 1, "page": 0, "size": 10}
    assert client.calls[1]["params"] == {"a": 1, "page": 1, "size": 10}


def test_empty_result() -> None:
    """Test that an empty data list returns an empty iterator."""
    client = DummyClient([{"data": []}])
    paginator = Paginator(client, "/p")
    assert list(paginator) == []


def test_custom_keys() -> None:
    """Test that custom data keys work."""
    client = DummyClient([{"custom_data": [1, 2]}])
    paginator = Paginator(client, "/p", data_key="custom_data")
    assert list(paginator) == [1, 2]


@pytest.mark.asyncio
async def test_async_paginator() -> None:
    """Test AsyncPaginator iteration."""
    client = AsyncDummyClient(
        [
            {"data": [1], "pagination": {"totalPages": 2}},
            {"data": [2], "pagination": {"totalPages": 2}},
        ]
    )
    paginator = AsyncPaginator(client, "/p", params={"a": 1}, page_size=10)  # type: ignore
    items = [item async for item in paginator]
    assert items == [1, 2]
    assert client.calls[0]["params"] == {"a": 1, "page": 0, "size": 10}
    assert client.calls[1]["params"] == {"a": 1, "page": 1, "size": 10}


@pytest.mark.asyncio
async def test_async_paginator_empty() -> None:
    """Test AsyncPaginator with empty results."""
    client = AsyncDummyClient([{"data": []}])
    paginator = AsyncPaginator(client, "/p")  # type: ignore
    items = [item async for item in paginator]
    assert items == []


def test_pagination_key_is_null() -> None:
    """Test handling of responses where 'pagination' is explicitly null."""
    client = DummyClient([{"data": [1, 2], "pagination": None}])
    paginator = Paginator(client, "/p")
    assert list(paginator) == [1, 2]


def test_json_list_paginator_success() -> None:
    """Test JsonListPaginator iteration over a list."""
    client = DummyClient([[1, 2]])
    paginator = JsonListPaginator(client, "/p", params={"a": 1})
    assert list(paginator) == [1, 2]
    # Verify params are passed as-is without pagination params
    assert client.calls[0]["params"] == {"a": 1}


def test_json_list_paginator_empty() -> None:
    """Test JsonListPaginator with empty list."""
    client = DummyClient([[]])
    paginator = JsonListPaginator(client, "/p")
    assert list(paginator) == []


def test_json_list_paginator_invalid_payload() -> None:
    """Test JsonListPaginator with non-list payload."""
    client = DummyClient([{"error": "bad"}])
    paginator = JsonListPaginator(client, "/p")
    assert list(paginator) == []


@pytest.mark.asyncio
async def test_async_json_list_paginator_success() -> None:
    """Test AsyncJsonListPaginator iteration over a list."""
    client = AsyncDummyClient([[1, 2]])
    paginator = AsyncJsonListPaginator(client, "/p", params={"a": 1})  # type: ignore
    items = [item async for item in paginator]
    assert items == [1, 2]
    # Verify params are passed as-is without pagination params
    assert client.calls[0]["params"] == {"a": 1}


@pytest.mark.asyncio
async def test_async_json_list_paginator_empty() -> None:
    """Test AsyncJsonListPaginator with empty list."""
    client = AsyncDummyClient([[]])
    paginator = AsyncJsonListPaginator(client, "/p")  # type: ignore
    items = [item async for item in paginator]
    assert items == []


@pytest.mark.asyncio
async def test_async_json_list_paginator_invalid_payload() -> None:
    """Test AsyncJsonListPaginator with non-list payload."""
    client = AsyncDummyClient([{"error": "bad"}])
    paginator = AsyncJsonListPaginator(client, "/p")  # type: ignore
    items = [item async for item in paginator]
    assert items == []
