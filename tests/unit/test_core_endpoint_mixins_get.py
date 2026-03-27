from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.core.endpoint.mixins.get import FilterGetEndpointMixin, PathGetEndpointMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    id: int


class DummyFilterGetEndpoint(FilterGetEndpointMixin[MockModel]):
    MODEL = MockModel
    PATH = "dummy"
    _id_param = "id"
    requires_study_key = True

    def __init__(self, items):
        self._items = items
        self._sync_client = MagicMock()
        self._async_client = AsyncMock()

    def _require_sync_client(self):
        return self._sync_client

    def _require_async_client(self):
        return self._async_client

    def _list_sync(self, client, paginator_cls, **kwargs):
        return self._items

    async def _list_async(self, client, paginator_cls, **kwargs):
        return self._items

    def _auto_filter(self, filters):
        return filters

    def _build_path(self, *args):
        return "/" + "/".join(str(a) for a in args)


def test_filter_get_endpoint_not_found_with_study_key():
    ep = DummyFilterGetEndpoint([])
    with pytest.raises(ValueError, match="MockModel 123 not found in study TEST_STUDY"):
        ep.get(study_key="TEST_STUDY", item_id=123)


@pytest.mark.asyncio
async def test_filter_get_endpoint_async_not_found_with_study_key():
    ep = DummyFilterGetEndpoint([])
    with pytest.raises(ValueError, match="MockModel 123 not found in study TEST_STUDY"):
        await ep.async_get(study_key="TEST_STUDY", item_id=123)


class DummyFilterGetEndpointNoStudy(DummyFilterGetEndpoint):
    requires_study_key = False


def test_filter_get_endpoint_not_found_without_study_key():
    ep = DummyFilterGetEndpointNoStudy([])
    with pytest.raises(ValueError, match="MockModel 123 not found"):
        ep.get(study_key=None, item_id=123)


class DummyPathGetEndpoint(PathGetEndpointMixin[MockModel]):
    MODEL = MockModel
    PATH = "items"
    requires_study_key = True

    def __init__(self):
        self._sync_client = MagicMock()
        self._async_client = AsyncMock()

    def _require_sync_client(self):
        return self._sync_client

    def _require_async_client(self):
        return self._async_client

    def _build_path(self, *args):
        return "/" + "/".join(str(a) for a in args)

    def _parse_item(self, data):
        return MockModel.model_validate(data)

    def _auto_filter(self, filters):
        return filters


def test_path_get_endpoint_requires_study_key():
    ep = DummyPathGetEndpoint()
    with pytest.raises(ValueError, match="Study key must be provided"):
        ep.get(study_key=None, item_id=123)


class DummyPathGetEndpointNoStudy(DummyPathGetEndpoint):
    requires_study_key = False
    PATH = ""


def test_path_get_endpoint_no_study_key_no_path():
    ep = DummyPathGetEndpointNoStudy()
    # It should generate path with just item_id
    assert ep._get_path_for_id(None, 123) == "/123"


def test_path_get_endpoint_raise_not_found():
    ep = DummyPathGetEndpoint()
    with pytest.raises(ValueError, match="MockModel not found"):
        ep._raise_not_found(study_key="TEST", item_id=123)


def test_filter_get_require_sync_client_raises():
    class IncompleteEndpoint(FilterGetEndpointMixin):
        MODEL = MockModel
        PATH = "dummy"

        def _auto_filter(self, filters):
            return filters

        def _build_path(self, *args):
            return ""

    ep = IncompleteEndpoint()
    with pytest.raises(NotImplementedError):
        ep._require_sync_client()

    with pytest.raises(NotImplementedError):
        ep._require_async_client()


def test_path_get_require_sync_client_raises():
    class IncompletePathEndpoint(PathGetEndpointMixin):
        MODEL = MockModel
        PATH = "dummy"

        def _auto_filter(self, filters):
            return filters

        def _build_path(self, *args):
            return ""

    ep = IncompletePathEndpoint()
    with pytest.raises(NotImplementedError):
        ep._require_sync_client()

    with pytest.raises(NotImplementedError):
        ep._require_async_client()


def test_validate_get_result_not_found():
    ep = DummyFilterGetEndpoint([])
    # Test require_study_key = True
    with pytest.raises(ValueError, match="MockModel 123 not found in study TEST_STUDY"):
        ep._validate_get_result([], "TEST_STUDY", 123)

    # Test require_study_key = False
    ep.requires_study_key = False
    with pytest.raises(ValueError, match="MockModel 123 not found"):
        ep._validate_get_result([], None, 123)


def test_path_get_endpoint_get():
    ep = DummyPathGetEndpoint()

    # Mock the internal operation methods instead
    ep._get_path_sync = MagicMock(return_value={"id": 123})

    result = ep.get(study_key="TEST_STUDY", item_id=123)
    assert result == {"id": 123}
    ep._get_path_sync.assert_called_once_with(ep._sync_client, study_key="TEST_STUDY", item_id=123)


@pytest.mark.asyncio
async def test_path_get_endpoint_async_get():
    ep = DummyPathGetEndpoint()

    # Mock the internal operation methods instead
    ep._get_path_async = AsyncMock(return_value={"id": 123})

    result = await ep.async_get(study_key="TEST_STUDY", item_id=123)
    assert result == {"id": 123}
    ep._get_path_async.assert_called_once_with(
        ep._async_client, study_key="TEST_STUDY", item_id=123
    )


def test_path_get_sync():
    ep = DummyPathGetEndpoint()

    # Mock execute_sync to bypass PathGetOperation execution
    with pytest.MonkeyPatch.context() as m:
        mock_execute = MagicMock(return_value={"id": 123})
        m.setattr(
            "imednet.core.endpoint.operations.get.PathGetOperation.execute_sync", mock_execute
        )

        result = ep._get_path_sync(ep._sync_client, study_key="TEST_STUDY", item_id=123)
        assert result == {"id": 123}


@pytest.mark.asyncio
async def test_path_get_async():
    ep = DummyPathGetEndpoint()

    # Mock execute_async to bypass PathGetOperation execution
    with pytest.MonkeyPatch.context() as m:
        mock_execute = AsyncMock(return_value={"id": 123})
        m.setattr(
            "imednet.core.endpoint.operations.get.PathGetOperation.execute_async", mock_execute
        )

        result = await ep._get_path_async(ep._async_client, study_key="TEST_STUDY", item_id=123)
        assert result == {"id": 123}


def test_list_sync_raises():
    class IncompleteEndpoint(FilterGetEndpointMixin):
        MODEL = MockModel
        PATH = "dummy"

        def _auto_filter(self, filters):
            return filters

        def _build_path(self, *args):
            return ""

    ep = IncompleteEndpoint()
    with pytest.raises(NotImplementedError):
        ep._list_sync(None, None)


@pytest.mark.asyncio
async def test_list_async_raises():
    class IncompleteEndpoint(FilterGetEndpointMixin):
        MODEL = MockModel
        PATH = "dummy"

        def _auto_filter(self, filters):
            return filters

        def _build_path(self, *args):
            return ""

    ep = IncompleteEndpoint()
    with pytest.raises(NotImplementedError):
        await ep._list_async(None, None)


def test_validate_get_result_found():
    ep = DummyFilterGetEndpoint([{"id": 123}])
    result = ep._validate_get_result([{"id": 123}], "TEST_STUDY", 123)
    assert result == {"id": 123}
