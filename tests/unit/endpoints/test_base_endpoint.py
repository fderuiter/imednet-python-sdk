from unittest.mock import MagicMock

import pytest

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.endpoint.base import GenericEndpoint, GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    pass


class MockEndpointImpl(EdcEndpointMixin, GenericEndpoint[MockModel]):
    PATH = "/test"
    MODEL = MockModel

    def __init__(self, client, ctx, async_client=None):
        super().__init__(client, ctx, async_client)


class MockListGetEndpoint(EdcEndpointMixin, GenericListGetEndpoint[MockModel]):
    PATH = "/items"
    MODEL = MockModel
    _id_param = "recordId"


class TestBaseEndpoint:
    @pytest.fixture
    def client(self):
        return MagicMock(spec=Client)

    @pytest.fixture
    def context(self):
        return Context()

    def test_require_async_client_raises(self, client, context):
        ep = MockEndpointImpl(client, context, async_client=None)
        with pytest.raises(RuntimeError, match="Async client not configured"):
            ep._require_async_client()

    def test_auto_filter_injects_study_key(self, client, context):
        context.set_default_study_key("DEFAULT")
        ep = MockEndpointImpl(client, context)

        filters = {"foo": "bar"}
        result = ep._auto_filter(filters)
        assert result["studyKey"] == "DEFAULT"
        assert result["foo"] == "bar"

    def test_auto_filter_preserves_existing_study_key(self, client, context):
        context.set_default_study_key("DEFAULT")
        ep = MockEndpointImpl(client, context)

        filters = {"studyKey": "EXPLICIT", "foo": "bar"}
        result = ep._auto_filter(filters)
        assert result["studyKey"] == "EXPLICIT"

    def test_camel_to_snake_handles_edge_cases(self, client, context):
        ep = MockListGetEndpoint(client, context)
        assert ep._camel_to_snake("HTTPResponse") == "http_response"
        assert ep._camel_to_snake("X") == "x"
        assert ep._camel_to_snake("already_snake") == "already_snake"

    def test_resolve_get_args_supports_kwargs(self, client, context):
        ep = MockListGetEndpoint(client, context)

        assert ep._resolve_get_args(None, None, {"study_key": "S1", "item_id": 7}) == ("S1", 7)
        assert ep._resolve_get_args(None, None, {"recordId": 9}) == (None, 9)
        assert ep._resolve_get_args(None, None, {"record_id": 11}) == (None, 11)

    def test_resolve_get_args_raises_on_bad_kwargs(self, client, context):
        ep = MockListGetEndpoint(client, context)

        with pytest.raises(TypeError, match="Unexpected keyword argument"):
            ep._resolve_get_args(None, 1, {"foo": "bar"})

        with pytest.raises(TypeError, match="Unexpected keyword argument"):
            ep._resolve_get_args(None, None, {"foo": "bar"})

        with pytest.raises(TypeError, match="Missing required argument: item_id"):
            ep._resolve_get_args(None, None, {})
