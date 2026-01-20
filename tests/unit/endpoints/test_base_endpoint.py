from typing import Any, List
from unittest.mock import MagicMock

import pytest

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.endpoints.base import BaseEndpoint


class MockItem:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockEndpointImpl(BaseEndpoint):
    PATH = "/test"

    def __init__(self, client, ctx, async_client=None, items=None):
        super().__init__(client, ctx, async_client)
        self.items = items or []

    def list(self, study_key: str) -> List[Any]:
        return self.items

    async def async_list(self, study_key: str) -> List[Any]:
        return self.items


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
