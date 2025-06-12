from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from imednet.core.client import AsyncClient, Client
from imednet.core.context import Context


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


@pytest.fixture
def context():
    return Context()


@pytest.fixture
def dummy_client():
    return MagicMock()


@pytest.fixture
def response_factory():
    def factory(data):
        return DummyResponse(data)

    return factory


@pytest.fixture
def paginator_factory(monkeypatch):
    def factory(module, items):
        captured = {"count": 0}

        class DummyPaginator:
            def __init__(self, client, path, params=None, page_size=100, **kwargs):
                captured["client"] = client
                captured["path"] = path
                captured["params"] = params or {}
                captured["page_size"] = page_size
                captured["count"] += 1
                self._items = items

            def __iter__(self):
                yield from self._items

        monkeypatch.setattr(module, "Paginator", DummyPaginator)
        return captured

    return factory


@pytest.fixture
def async_paginator_factory(monkeypatch):
    def factory(module, items):
        captured = {"count": 0}

        class DummyPaginator:
            def __init__(self, client, path, params=None, page_size=100, **kwargs):
                captured["client"] = client
                captured["path"] = path
                captured["params"] = params or {}
                captured["page_size"] = page_size
                captured["count"] += 1
                self._items = items

            async def __aiter__(self):
                for item in self._items:
                    yield item

        monkeypatch.setattr(module, "AsyncPaginator", DummyPaginator)
        return captured

    return factory


@pytest.fixture
def patch_build_filter(monkeypatch):
    def patch(module):
        captured = {}

        def fake(filters):
            captured["filters"] = filters
            return "FILTERED"

        monkeypatch.setattr(module, "build_filter_string", fake)
        return captured

    return patch


@pytest.fixture
def http_client():
    return Client("key", "secret", base_url="https://api.test")


@pytest_asyncio.fixture
async def async_http_client():
    client = AsyncClient("key", "secret", base_url="https://api.test")
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def respx_mock_client(http_client, respx_mock):
    respx_mock.base_url = http_client.base_url
    return respx_mock


@pytest_asyncio.fixture
async def respx_mock_async_client(async_http_client, respx_mock):
    respx_mock.base_url = async_http_client.base_url
    return respx_mock


@pytest.fixture
def sample_data():
    return {"data": [1]}
