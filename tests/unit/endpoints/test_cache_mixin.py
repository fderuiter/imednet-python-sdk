from unittest.mock import MagicMock

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins.cache import CachedEndpointMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    pass


class MockCachedEndpoint(
    EdcEndpointMixin, CachedEndpointMixin[MockModel], GenericListGetEndpoint[MockModel]
):
    PATH = "/test"
    MODEL = MockModel


def test_cache_mixin_lazy_initialization():
    ctx = Context()
    ep = MockCachedEndpoint(MagicMock(spec=Client), ctx)
    assert not hasattr(ep, "_cache")
    assert ep._get_local_cache() == {}
    assert hasattr(ep, "_cache")
