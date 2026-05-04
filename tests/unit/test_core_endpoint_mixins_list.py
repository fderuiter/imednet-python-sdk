from unittest.mock import AsyncMock, MagicMock

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
