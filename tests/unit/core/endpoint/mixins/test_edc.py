import pytest
from unittest.mock import MagicMock

from imednet.core.context import Context
from imednet.core.endpoint.mixins.edc import EdcEndpointMixin

class MockEdcEndpoint(EdcEndpointMixin):
    def __init__(self, ctx):
        self._ctx = ctx

class TestEdcEndpointMixin:
    @pytest.fixture
    def context(self):
        return Context()

    def test_auto_filter_injects_study_key(self, context):
        context.set_default_study_key("DEFAULT")
        ep = MockEdcEndpoint(context)

        filters = {"foo": "bar"}
        result = ep._auto_filter(filters)
        assert result["studyKey"] == "DEFAULT"
        assert result["foo"] == "bar"

    def test_auto_filter_preserves_existing_study_key(self, context):
        context.set_default_study_key("DEFAULT")
        ep = MockEdcEndpoint(context)

        filters = {"studyKey": "EXPLICIT", "foo": "bar"}
        result = ep._auto_filter(filters)
        assert result["studyKey"] == "EXPLICIT"
