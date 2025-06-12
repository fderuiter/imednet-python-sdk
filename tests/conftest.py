from unittest.mock import MagicMock

import pytest
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
        captured = {}

        class DummyPaginator:
            def __init__(self, client, path, params=None, page_size=100, **kwargs):
                captured["client"] = client
                captured["path"] = path
                captured["params"] = params or {}
                captured["page_size"] = page_size
                self._items = items

            def __iter__(self):
                yield from self._items

        monkeypatch.setattr(module, "Paginator", DummyPaginator)
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
