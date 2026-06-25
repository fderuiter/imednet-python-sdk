# ruff: noqa: E402

"""Conftest module."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

ROOT = Path(__file__).resolve().parents[1]
LIVE_TESTS_DIR = (ROOT / "tests" / "live").resolve()
for source_root in (
    ROOT / "packages" / "core" / "src",
    ROOT / "packages" / "plugins-workflows" / "src",
    ROOT / "packages" / "providers-airflow" / "src",
):
    sys.path.insert(0, str(source_root))

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context, clear_study_context


@pytest.fixture(autouse=True)
def block_external_requests(request: pytest.FixtureRequest):
    """Block real network calls in all non-live tests.

    Uses the ``respx_mock`` pytest-plugin fixture so that all non-live tests
    share a single strict router; tests cannot bypass the guard by opening
    their own ``respx.mock`` context or decorator.
    """
    if _is_live_test(request.node):
        yield
        return
    request.getfixturevalue("respx_mock")
    yield


def _is_live_test(node: object) -> bool:
    """Test the is live test functionality."""
    if not hasattr(node, "get_closest_marker"):
        return False

    if node.get_closest_marker("live"):
        return True

    node_path = getattr(node, "path", None)
    if node_path is None:
        return False

    return Path(str(node_path)).resolve().is_relative_to(LIVE_TESTS_DIR)


@pytest.fixture(autouse=True)
def reset_study_context_between_tests():
    """Test the reset study context between tests functionality."""
    clear_study_context()
    yield
    clear_study_context()


@pytest.fixture(autouse=True)
def reset_circuit_breaker_between_tests():
    """Test the reset circuit breaker between tests functionality."""
    from imednet.core.operations.circuit_breaker import get_global_circuit_breaker

    get_global_circuit_breaker().reset()
    yield
    get_global_circuit_breaker().reset()


class DummyResponse:
    """Test suite for DummyResponse."""

    def __init__(self, data):
        """Initialize a new instance."""
        self._data = data

    def json(self):
        """Test the json functionality."""
        return self._data


@pytest.fixture
def context():
    """Test the context functionality."""
    return Context()


@pytest.fixture
def dummy_client():
    """Test the dummy client functionality."""
    return MagicMock()


@pytest.fixture
def response_factory():
    """Test the response factory functionality."""

    def factory(data):
        """Test the factory functionality."""
        return DummyResponse(data)

    return factory


@pytest.fixture
def paginator_factory(monkeypatch):
    """Test the paginator factory functionality."""
    from imednet.core.endpoint.operations.list import ListOperation
    from tests.utils.streaming import StreamingMockWrapper

    def factory(module, items):
        """Test the factory functionality."""
        captured = {"count": 0}

        class DummyPaginator:
            """Test suite for DummyPaginator."""

            def __init__(self, client, path, params=None, page_size=100, **kwargs):
                """Initialize a new instance."""
                captured["client"] = client
                captured["path"] = path
                captured["params"] = params or {}
                captured["page_size"] = page_size
                captured["count"] += 1
                self._items = items

            def __iter__(self):
                """Test the iter functionality."""
                yield from self._items

        from imednet.core.endpoint.base import SyncListGetEndpoint

        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, SyncListGetEndpoint):
                monkeypatch.setattr(obj, "PAGINATOR_CLS", DummyPaginator, raising=False)

        def fake_execute_sync(self, client, paginator_cls):
            """Test the fake execute sync functionality."""
            paginator = paginator_cls(
                client, self.path, params=self.params, page_size=self.page_size
            )
            parsed_items = [self.parse_func(item) for item in paginator._items]
            return StreamingMockWrapper(parsed_items)

        monkeypatch.setattr(ListOperation, "execute_sync", fake_execute_sync)
        return captured

    return factory


@pytest.fixture
def async_paginator_factory(monkeypatch):
    """Test the async paginator factory functionality."""
    from imednet.core.endpoint.operations.list import ListOperation
    from tests.utils.streaming import StreamingMockWrapper

    def factory(module, items):
        """Test the factory functionality."""
        captured = {"count": 0}

        class DummyPaginator:
            """Test suite for DummyPaginator."""

            def __init__(self, client, path, params=None, page_size=100, **kwargs):
                """Initialize a new instance."""
                captured["client"] = client
                captured["path"] = path
                captured["params"] = params or {}
                captured["page_size"] = page_size
                captured["count"] += 1
                self._items = items

            async def __aiter__(self):
                """Implementation detail."""
                for item in self._items:
                    yield item

        from imednet.core.endpoint.base import AsyncListGetEndpoint

        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, AsyncListGetEndpoint):
                monkeypatch.setattr(obj, "ASYNC_PAGINATOR_CLS", DummyPaginator, raising=False)

        def fake_execute_async(self, client, paginator_cls):
            """Test the fake execute async functionality."""
            paginator = paginator_cls(
                client, self.path, params=self.params, page_size=self.page_size
            )
            parsed_items = [self.parse_func(item) for item in paginator._items]
            return StreamingMockWrapper(parsed_items)

        monkeypatch.setattr(ListOperation, "execute_async", fake_execute_async)

        return captured

    return factory


@pytest.fixture
def patch_build_filter(monkeypatch):
    """Test the patch build filter functionality."""

    def patch(module):
        """Test the patch functionality."""
        captured = {}

        def fake(filters):
            """Test the fake functionality."""
            captured["filters"] = filters
            return "FILTERED"

        if hasattr(module, "build_filter_string"):
            monkeypatch.setattr(module, "build_filter_string", fake)
        else:
            import imednet.core.endpoint.base as endpoint_base

            monkeypatch.setattr(endpoint_base, "build_filter_string", fake)
        return captured

    return patch


@pytest.fixture
def http_client():
    """Test the http client functionality."""
    return Client("key", "secret", base_url="https://api.test")


@pytest_asyncio.fixture
async def async_http_client():
    """Implementation detail."""
    client = AsyncClient("key", "secret", base_url="https://api.test")
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def respx_mock_client(http_client, respx_mock):
    """Test the respx mock client functionality."""
    respx_mock.base_url = http_client.base_url
    return respx_mock


@pytest_asyncio.fixture
async def respx_mock_async_client(async_http_client, respx_mock):
    """Implementation detail."""
    respx_mock.base_url = async_http_client.base_url
    return respx_mock


@pytest.fixture
def sample_data():
    """Test the sample data functionality."""
    return {"data": [1]}
