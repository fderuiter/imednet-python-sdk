"""Unit tests for async paginator."""

import pytest

from imednet.core.paginator import AsyncPaginator


class DummyAsyncClient:
    """Test suite for DummyAsyncClient."""

    def __init__(self, responses):
        """Initialize the test object."""
        self.responses = responses
        self.calls = []

    async def get(self, path, params=None):
        """Helper function to get."""
        self.calls.append({"path": path, "params": params})
        data = self.responses.pop(0)
        return type("Resp", (), {"json": lambda self, d=data: d})()


@pytest.mark.asyncio
async def test_iterates_pages():
    """Test that iterates pages asynchronously."""
    client = DummyAsyncClient(
        [
            {"data": [1], "pagination": {"totalPages": 2}},
            {"data": [2], "pagination": {"totalPages": 2}},
        ]
    )
    paginator = AsyncPaginator(client, "/items", page_size=10)

    items = []
    async for item in paginator:
        items.append(item)

    assert items == [1, 2]
    assert client.calls[0]["params"] == {"page": 0, "size": 10}
    assert client.calls[1]["params"] == {"page": 1, "size": 10}
