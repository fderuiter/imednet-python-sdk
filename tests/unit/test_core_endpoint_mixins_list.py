from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.core.endpoint.mixins.list import ListEndpointMixin
from imednet.core.endpoint.structs import ParamState
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    id: int
    name: str = ""


class DummyListEndpoint(ListEndpointMixin[MockModel]):
    MODEL = MockModel
    PATH = "dummy"
    requires_study_key = True

    def __init__(self, items=None):
        self._items = items or []
        self._sync_client = MagicMock()
        self._async_client = AsyncMock()

    def _require_sync_client(self):
        return self._sync_client

    def _require_async_client(self):
        return self._async_client

    def _build_path(self, *segments):
        return "/".join(filter(None, segments))

    def _auto_filter(self, data):
        return data

    def _resolve_params(self, study_key, extra_params, filters):
        return ParamState(study=study_key, params=extra_params or {}, other_filters=filters)

    def _get_local_cache(self):
        return None

    def _check_cache_hit(self, study, refresh, other_filters, cache):
        return None

    def _update_local_cache(self, result, study, has_filters):
        pass


def test_list_by_attribute_filters_correctly():
    """Test that list_by_attribute successfully filters items based on the provided attribute."""
    endpoint = DummyListEndpoint()
    # Mock the public `list` method which list_by_attribute calls internally
    endpoint.list = MagicMock(
        return_value=[
            MockModel(id=1, name="first"),
            MockModel(id=2, name="second"),
            MockModel(id=3, name="first"),
        ]
    )

    result = endpoint.list_by_attribute("name", "first", study_key="test_study")

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 3
    endpoint.list.assert_called_once_with("test_study")


@pytest.mark.asyncio
async def test_async_list_by_attribute_filters_correctly():
    """Test that async_list_by_attribute successfully filters items based on the provided attribute."""
    endpoint = DummyListEndpoint()

    # Mock the public `async_list` method
    async def mock_async_list(*args, **kwargs):
        return [
            MockModel(id=4, name="async_first"),
            MockModel(id=5, name="async_second"),
            MockModel(id=6, name="async_first"),
        ]

    endpoint.async_list = mock_async_list

    result = await endpoint.async_list_by_attribute("name", "async_first", study_key="test_study")

    assert len(result) == 2
    assert result[0].id == 4
    assert result[1].id == 6
