import inspect
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

    def test_get_signature_is_explicit(self, client, context):
        ep = MockListGetEndpoint(client, context)
        signature = inspect.signature(ep.get)

        assert list(signature.parameters.keys()) == ["study_key", "item_id"]

    def test_get_requires_item_id(self, client, context):
        ep = MockListGetEndpoint(client, context)

        with pytest.raises(TypeError, match="Missing required argument: item_id"):
            ep.get("S1", None)

    def test_parameter_processing_is_independent(self, client, context):
        ep = MockListGetEndpoint(client, context)

        # Mock the param processor
        mock_processor = MagicMock()
        mock_processor.process_filters.return_value = ({"processed": "yes"}, {"special": 1})
        ep.PARAM_PROCESSOR = mock_processor

        # Mock the study key strategy
        mock_strategy = MagicMock()
        mock_strategy.process.return_value = ("STUDY1", {"processed": "yes", "other": "val"})
        ep.STUDY_KEY_STRATEGY = mock_strategy

        # Call the internal resolution hook directly
        filters = {"raw": "filter"}
        extra_params = {"extra": 2}
        param_state = ep._resolve_params("STUDY_KEY", extra_params, filters)

        # Verify the hooks were invoked independently of any data execution
        mock_processor.process_filters.assert_called_once()
        mock_strategy.process.assert_called_once()

        # Check the resulting param state
        assert param_state.study == "STUDY1"
        assert param_state.params["special"] == 1
        assert param_state.params["extra"] == 2
        assert "filter" in param_state.params
        assert param_state.other_filters == {"processed": "yes", "other": "val"}
