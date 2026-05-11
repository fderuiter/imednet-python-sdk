import asyncio
from unittest.mock import MagicMock

import pytest

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.endpoint.base import GenericEndpoint, GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    pass


class MockEndpointImpl(EdcEndpointMixin, GenericListGetEndpoint[MockModel]):
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

    def test_get_local_cache_not_enabled(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep._enable_cache = False
        assert ep._get_local_cache() is None

    def test_get_local_cache_enabled(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep._enable_cache = True
        ep._cache = {"STUDY": [MockModel()]}
        assert ep._get_local_cache() == {"STUDY": ep._cache["STUDY"]}

    def test_update_local_cache(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep._enable_cache = True
        ep.requires_study_key = True

        # Test basic
        result = [MockModel()]
        ep._update_local_cache(result, "STUDY", False)
        assert ep._cache == {"STUDY": result}

        # Test study none does nothing for study cache
        ep._cache = None
        ep._update_local_cache(result, None, False)
        assert ep._cache == {}

        # Test not study key cache
        ep.requires_study_key = False
        ep._cache = None
        ep._update_local_cache(result, None, False)
        assert ep._cache == result

        # Test with filters
        ep._cache = None
        ep._update_local_cache(result, None, True)
        assert ep._cache is None

    def test_check_cache_hit(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep._enable_cache = True

        models = [MockModel()]

        # Test study key required cache hit
        ep.requires_study_key = True
        cache = {"STUDY": models}
        assert ep._check_cache_hit("STUDY", False, {}, cache) == models

        # Test study key required cache miss
        assert ep._check_cache_hit("OTHER", False, {}, cache) is None

        # Test no study key cache hit
        ep.requires_study_key = False
        cache = models
        assert ep._check_cache_hit(None, False, {}, cache) == models

        # Test refresh
        assert ep._check_cache_hit(None, True, {}, cache) is None

        # Test filters
        assert ep._check_cache_hit(None, False, {"foo": "bar"}, cache) is None

        # Test disabled cache
        ep._enable_cache = False
        assert ep._check_cache_hit(None, False, {}, cache) is None

    def test_resolve_params(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep.PARAM_PROCESSOR = ep.param_processor
        ep.STUDY_KEY_STRATEGY = ep.study_key_strategy
        ep.requires_study_key = True

        # Test basic resolution
        state = ep._resolve_params("STUDY123", None, {"foo": "bar"})
        assert state.study == "STUDY123"
        assert "filter" in state.params
        assert "studyKey==STUDY123" in state.params["filter"]
        assert "foo==bar" in state.params["filter"]
        assert state.other_filters == {"foo": "bar"}

        # Test extra params and special params
        state = ep._resolve_params("STUDY123", {"extra": "param"}, {"special": "val"})
        assert state.study == "STUDY123"
        assert state.params["extra"] == "param"

    def test_resolve_params_missing_study_key(self, client, context):
        from imednet.errors import ClientError

        ep = MockEndpointImpl(client, context)
        ep.PARAM_PROCESSOR = ep.param_processor
        ep.STUDY_KEY_STRATEGY = ep.study_key_strategy
        ep.requires_study_key = True

        with pytest.raises(ClientError, match="Study key must be provided"):
            ep._resolve_params(None, None, {})

    def test_get_local_cache_requires_study_key_initializes(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep._enable_cache = True
        ep.requires_study_key = True
        ep._cache = None
        assert ep._get_local_cache() == {}

    def test_list_sync(self, client, context, monkeypatch):
        ep = MockEndpointImpl(client, context)
        mock_list = MagicMock(return_value=[MockModel()])
        monkeypatch.setattr(ep, "_list_sync", mock_list)

        result = ep.list("STUDY123", foo="bar")
        mock_list.assert_called_once_with(client, ep.PAGINATOR_CLS, study_key="STUDY123", foo="bar")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_async_list(self, client, context, monkeypatch):
        async_client = MagicMock()
        ep = MockEndpointImpl(client, context, async_client)
        import asyncio

        f = asyncio.Future()
        f.set_result([MockModel()])
        mock_list = MagicMock(return_value=f)
        monkeypatch.setattr(ep, "_list_async", mock_list)

        result = await ep.async_list("STUDY123", foo="bar")
        mock_list.assert_called_once_with(
            async_client, ep.ASYNC_PAGINATOR_CLS, study_key="STUDY123", foo="bar"
        )
        assert len(result) == 1

    def test_get_sync(self, client, context, monkeypatch):
        ep = MockEndpointImpl(client, context)
        mock_get = MagicMock(return_value=MockModel())
        monkeypatch.setattr(ep, "_get_sync", mock_get)

        result = ep.get("STUDY123", 1)
        mock_get.assert_called_once_with(client, ep.PAGINATOR_CLS, study_key="STUDY123", item_id=1)
        assert result is not None

    @pytest.mark.asyncio
    async def test_async_get(self, client, context, monkeypatch):
        async_client = MagicMock()
        ep = MockEndpointImpl(client, context, async_client)
        f = asyncio.Future()
        f.set_result(MockModel())
        mock_get = MagicMock(return_value=f)
        monkeypatch.setattr(ep, "_get_async", mock_get)

        result = await ep.async_get("STUDY123", 1)
        mock_get.assert_called_once_with(
            async_client, ep.ASYNC_PAGINATOR_CLS, study_key="STUDY123", item_id=1
        )
        assert result is not None

    def test_validate_get_result(self, client, context):
        ep = MockEndpointImpl(client, context)
        model = MockModel()

        # Test success
        result = ep._validate_get_result([model], "STUDY123", 1)
        assert result == model

        # Test missing raises
        from imednet.errors import NotFoundError

        with pytest.raises(NotFoundError, match="MockModel 1 not found in study STUDY123"):
            ep._validate_get_result([], "STUDY123", 1)

    def test_list_operations(self, client, context, monkeypatch):
        ep = MockEndpointImpl(client, context)

        # Test _list_sync
        monkeypatch.setattr(
            ep,
            "_prepare_list_request",
            MagicMock(return_value=MagicMock(cached_result=[MockModel()])),
        )
        result = ep._list_sync(client, ep.PAGINATOR_CLS)
        assert len(result) == 1

        # Test _list_sync cache miss
        state = MagicMock(
            cached_result=None, path="path", params={}, study="STUDY", has_filters=False
        )
        monkeypatch.setattr(ep, "_prepare_list_request", MagicMock(return_value=state))

        mock_execute = MagicMock(return_value=[MockModel()])
        import imednet.core.endpoint.base

        monkeypatch.setattr(imednet.core.endpoint.base.ListOperation, "execute_sync", mock_execute)
        monkeypatch.setattr(ep, "_update_local_cache", MagicMock())

        result = ep._list_sync(client, ep.PAGINATOR_CLS)
        assert len(result) == 1
        ep._update_local_cache.assert_called_once_with([result[0]], "STUDY", False)

    @pytest.mark.asyncio
    async def test_async_list_operations(self, client, context, monkeypatch):
        async_client = MagicMock()
        ep = MockEndpointImpl(client, context, async_client)

        # Test _list_async cache hit
        monkeypatch.setattr(
            ep,
            "_prepare_list_request",
            MagicMock(return_value=MagicMock(cached_result=[MockModel()])),
        )
        result = await ep._list_async(async_client, ep.ASYNC_PAGINATOR_CLS)
        assert len(result) == 1

        # Test _list_async cache miss
        state = MagicMock(
            cached_result=None, path="path", params={}, study="STUDY", has_filters=False
        )
        monkeypatch.setattr(ep, "_prepare_list_request", MagicMock(return_value=state))

        f = asyncio.Future()
        f.set_result([MockModel()])
        mock_execute = MagicMock(return_value=f)
        import imednet.core.endpoint.base

        monkeypatch.setattr(imednet.core.endpoint.base.ListOperation, "execute_async", mock_execute)
        monkeypatch.setattr(ep, "_update_local_cache", MagicMock())

        result = await ep._list_async(async_client, ep.ASYNC_PAGINATOR_CLS)
        assert len(result) == 1
        ep._update_local_cache.assert_called_once_with([result[0]], "STUDY", False)

    def test_get_operations(self, client, context, monkeypatch):
        ep = MockEndpointImpl(client, context)

        # Test _get_sync
        mock_execute = MagicMock(return_value=MockModel())
        import imednet.core.endpoint.base

        monkeypatch.setattr(
            imednet.core.endpoint.base.FilterGetOperation, "execute_sync", mock_execute
        )

        result = ep._get_sync(client, ep.PAGINATOR_CLS, study_key="STUDY", item_id=1)
        assert result is not None
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_get_operations(self, client, context, monkeypatch):
        async_client = MagicMock()
        ep = MockEndpointImpl(client, context, async_client)

        # Test _get_async
        f = asyncio.Future()
        f.set_result(MockModel())
        mock_execute = MagicMock(return_value=f)
        import imednet.core.endpoint.base

        monkeypatch.setattr(
            imednet.core.endpoint.base.FilterGetOperation, "execute_async", mock_execute
        )

        result = await ep._get_async(
            async_client, ep.ASYNC_PAGINATOR_CLS, study_key="STUDY", item_id=1
        )
        assert result is not None
        mock_execute.assert_called_once()

    def test_prepare_list_request(self, client, context, monkeypatch):
        ep = MockEndpointImpl(client, context)

        # Mock dependencies
        mock_resolve_params = MagicMock()
        mock_resolve_params.return_value = MagicMock(study="STUDY", params={}, other_filters={})
        monkeypatch.setattr(ep, "_resolve_params", mock_resolve_params)

        mock_get_local_cache = MagicMock()
        mock_get_local_cache.return_value = {}
        monkeypatch.setattr(ep, "_get_local_cache", mock_get_local_cache)

        mock_check_cache_hit = MagicMock()
        monkeypatch.setattr(ep, "_check_cache_hit", mock_check_cache_hit)

        mock_get_endpoint_path = MagicMock()
        mock_get_endpoint_path.return_value = "path"
        monkeypatch.setattr(ep, "_get_endpoint_path", mock_get_endpoint_path)

        # Test cache hit
        mock_check_cache_hit.return_value = [MockModel()]
        state = ep._prepare_list_request("STUDY", None, {}, False)
        assert state.cached_result is not None
        assert state.study == "STUDY"
        assert state.has_filters is False

        # Test cache miss
        mock_check_cache_hit.return_value = None
        state = ep._prepare_list_request("STUDY", None, {}, False)
        assert state.cached_result is None
        assert state.path == "path"
        assert state.params == {}

    def test_generic_endpoint_build_path(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep.PATH = "test"
        assert ep._build_path(1, "extra") == "/api/v1/edc/studies/1/extra"

        ep.PATH = ""
        assert ep._build_path(1, "extra") == "/api/v1/edc/studies/1/extra"

    def test_generic_endpoint_auto_filter(self, client, context):
        ep = MockEndpointImpl(client, context)
        filters = {"foo": "bar"}
        assert ep._auto_filter(filters) == filters

    def test_generic_endpoint_require_sync_client(self, client, context):
        ep = MockEndpointImpl(client, context)
        assert ep._require_sync_client() == client

    def test_generic_endpoint_require_async_client(self, client, context):
        async_client = MagicMock()
        ep = MockEndpointImpl(client, context, async_client)
        assert ep._require_async_client() == async_client

    def test_generic_endpoint_require_async_client_raises(self, client, context):
        ep = MockEndpointImpl(client, context)
        with pytest.raises(RuntimeError, match="Async client not configured"):
            ep._require_async_client()

    def test_generic_endpoint_parse_item(self, client, context):
        ep = MockEndpointImpl(client, context)
        item = {"foo": "bar"}
        # Just ensure it calls get_model_parser correctly (implicitly tested)
        # Mocking get_model_parser is easier
        import imednet.core.endpoint.base

        mock_parser = MagicMock(return_value=MockModel())
        mock_get_parser = MagicMock(return_value=mock_parser)

        original_get_parser = imednet.core.endpoint.base.get_model_parser
        imednet.core.endpoint.base.get_model_parser = mock_get_parser

        try:
            result = ep._parse_item(item)
            assert isinstance(result, MockModel)
            mock_get_parser.assert_called_once_with(ep.MODEL)
            mock_parser.assert_called_once_with(item)

            assert ep._resolve_parse_func() == ep._parse_item
        finally:
            imednet.core.endpoint.base.get_model_parser = original_get_parser

    def test_generic_endpoint_param_processor_cls(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep.PARAM_PROCESSOR = None
        from imednet.core.endpoint.strategies import DefaultParamProcessor

        ep.PARAM_PROCESSOR_CLS = DefaultParamProcessor
        assert isinstance(ep.param_processor, DefaultParamProcessor)

    def test_generic_endpoint_resolve_params_extra_params(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep.requires_study_key = True

        from imednet.core.endpoint.strategies import DefaultParamProcessor

        class SpecialParamProcessor(DefaultParamProcessor):
            def process_filters(self, filters):
                return filters, {"special": "val"}

        ep.PARAM_PROCESSOR_CLS = SpecialParamProcessor

        # extra_params is None
        state = ep._resolve_params("STUDY123", None, {})
        assert state.params["special"] == "val"

        # extra_params is dict
        state = ep._resolve_params("STUDY123", {"existing": "param"}, {})
        assert state.params["existing"] == "param"
        assert state.params["special"] == "val"

    def test_generic_endpoint_build_path_empty_base(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep.BASE_PATH = ""
        assert ep._build_path(1, "extra") == "/1/extra"

    def test_study_key_strategy_cls(self, client, context):
        ep = MockEndpointImpl(client, context)
        ep.STUDY_KEY_STRATEGY = None
        ep.requires_study_key = False
        from imednet.core.endpoint.strategies import OptionalStudyKeyStrategy

        assert isinstance(ep.study_key_strategy, OptionalStudyKeyStrategy)

    def test_generic_endpoint_auto_filter_direct(self, client, context):
        ep = MockEndpointImpl(client, context)
        filters = {"foo": "bar"}
        assert ep._auto_filter(filters) == filters

    def test_generic_endpoint_base_auto_filter(self, client, context):
        class TestEndpoint(GenericEndpoint[MockModel]):
            PATH = "test"
            MODEL = MockModel

        ep = TestEndpoint(client, context)
        filters = {"foo": "bar"}
        assert ep._auto_filter(filters) == filters
