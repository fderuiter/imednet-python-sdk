"""TODO: Add docstring."""

import inspect
from unittest.mock import MagicMock

import pytest

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.endpoint.base import GenericEndpoint, GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    """TODO: Add docstring."""

    pass


class MockEndpointImpl(EdcEndpointMixin, GenericEndpoint[MockModel]):
    """TODO: Add docstring."""

    PATH = "/test"
    MODEL = MockModel

    def __init__(self, client, ctx, async_client=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx, async_client)


class MockListGetEndpoint(EdcEndpointMixin, GenericListGetEndpoint[MockModel]):
    """TODO: Add docstring."""

    PATH = "/items"
    MODEL = MockModel
    _id_param = "recordId"


class TestBaseEndpoint:
    """TODO: Add docstring."""

    @pytest.fixture
    def client(self):
        """TODO: Add docstring."""
        return MagicMock(spec=Client)

    @pytest.fixture
    def context(self):
        """TODO: Add docstring."""
        return Context()

    def test_require_async_client_raises(self, client, context):
        """TODO: Add docstring."""
        ep = MockEndpointImpl(client, context, async_client=None)
        with pytest.raises(RuntimeError, match="Async client not configured"):
            ep._require_async_client()

    def test_auto_filter_injects_study_key(self, client, context):
        """TODO: Add docstring."""
        context.set_default_study_key("DEFAULT")
        ep = MockEndpointImpl(client, context)

        filters = {"foo": "bar"}
        result = ep._auto_filter(filters)
        assert result["studyKey"] == "DEFAULT"
        assert result["foo"] == "bar"

    def test_auto_filter_preserves_existing_study_key(self, client, context):
        """TODO: Add docstring."""
        context.set_default_study_key("DEFAULT")
        ep = MockEndpointImpl(client, context)

        filters = {"studyKey": "EXPLICIT", "foo": "bar"}
        result = ep._auto_filter(filters)
        assert result["studyKey"] == "EXPLICIT"

    def test_get_signature_is_explicit(self, client, context):
        """TODO: Add docstring."""
        ep = MockListGetEndpoint(client, context)
        signature = inspect.signature(ep.get)

        assert list(signature.parameters.keys()) == ["study_key", "item_id"]

    def test_get_requires_item_id(self, client, context):
        """TODO: Add docstring."""
        ep = MockListGetEndpoint(client, context)

        with pytest.raises(TypeError, match="Missing required argument: item_id"):
            ep.get("S1", None)
