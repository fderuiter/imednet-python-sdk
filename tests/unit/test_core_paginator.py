from typing import Any, Dict, List

import pytest

from imednet.core.paginator import AsyncSimpleListPaginator, Paginator, SimpleListPaginator


class DummyClient:
    def __init__(self, responses: List[Any]):
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []

    def get(self, path: str, params: Dict[str, Any] | None = None):
        self.calls.append({"path": path, "params": params})
        data = self.responses.pop(0)
        return type("Resp", (), {"json": lambda self: data})()


class AsyncDummyClient:
    def __init__(self, responses: List[Any]):
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


def test_simple_list_paginator_flat_list() -> None:
    client = DummyClient([[1, 2, 3]])
    paginator = SimpleListPaginator(client, "/flat")
    assert list(paginator) == [1, 2, 3]


def test_simple_list_paginator_wrapped() -> None:
    client = DummyClient([{"data": [4, 5]}])
    paginator = SimpleListPaginator(client, "/wrapped")
    assert list(paginator) == [4, 5]


@pytest.mark.asyncio
async def test_async_simple_list_paginator() -> None:
    client = AsyncDummyClient([[10, 20]])
    paginator = AsyncSimpleListPaginator(client, "/async-flat")
    results = []
    async for item in paginator:
        results.append(item)
    assert results == [10, 20]
