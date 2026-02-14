from unittest.mock import MagicMock

import pytest

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.endpoint.base import BaseEndpoint
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    pass


class MockEndpointImpl(BaseEndpoint[MockModel]):
    PATH = "/test"
    MODEL = MockModel

    def __init__(self, client, ctx, async_client=None):
        super().__init__(client, ctx, async_client)


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

    def test_auto_filter_does_nothing(self, client, context):
        """Verify generic BaseEndpoint does not inject filters."""
        context.set_default_study_key("DEFAULT")
        ep = MockEndpointImpl(client, context)

        filters = {"foo": "bar"}
        result = ep._auto_filter(filters)
        # Should be unchanged
        assert result == filters
        assert "studyKey" not in result
