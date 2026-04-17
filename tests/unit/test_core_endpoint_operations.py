from unittest.mock import AsyncMock, MagicMock

import pytest
from imednet.errors import ClientError, NotFoundError

from imednet.constants import HEADER_EMAIL_NOTIFY
from imednet.core.endpoint.operations.filter_get import FilterGetOperation
from imednet.core.endpoint.operations.get import PathGetOperation
from imednet.core.endpoint.operations.list import ListOperation
from imednet.core.endpoint.operations.record_create import RecordCreateOperation


def dummy_parse_func(data):
    return data


def test_path_get_operation_execute_sync():
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"id": 1, "name": "Test"}
    client.get.return_value = response

    not_found_func = MagicMock()

    operation = PathGetOperation(
        path="/test", parse_func=dummy_parse_func, not_found_func=not_found_func
    )

    result = operation.execute_sync(client)

    assert result == {"id": 1, "name": "Test"}
    client.get.assert_called_once_with("/test")
    not_found_func.assert_not_called()


def test_path_get_operation_execute_sync_not_found():
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = None
    client.get.return_value = response

    not_found_func = MagicMock(side_effect=NotFoundError("Not found"))

    operation = PathGetOperation(
        path="/test", parse_func=dummy_parse_func, not_found_func=not_found_func
    )

    with pytest.raises(NotFoundError, match="Not found"):
        operation.execute_sync(client)

    client.get.assert_called_once_with("/test")
    not_found_func.assert_called_once()


@pytest.mark.asyncio
async def test_path_get_operation_execute_async():
    client = AsyncMock()
    response = MagicMock()
    response.json.return_value = {"id": 1, "name": "Test"}
    client.get.return_value = response

    not_found_func = MagicMock()

    operation = PathGetOperation(
        path="/test", parse_func=dummy_parse_func, not_found_func=not_found_func
    )

    result = await operation.execute_async(client)

    assert result == {"id": 1, "name": "Test"}
    client.get.assert_called_once_with("/test")
    not_found_func.assert_not_called()


@pytest.mark.asyncio
async def test_path_get_operation_execute_async_not_found():
    client = AsyncMock()
    response = MagicMock()
    response.json.return_value = None
    client.get.return_value = response

    not_found_func = MagicMock(side_effect=NotFoundError("Not found"))

    operation = PathGetOperation(
        path="/test", parse_func=dummy_parse_func, not_found_func=not_found_func
    )

    with pytest.raises(NotFoundError, match="Not found"):
        await operation.execute_async(client)

    client.get.assert_called_once_with("/test")
    not_found_func.assert_called_once()


def test_list_operation_sync():
    client = MagicMock()
    paginator_cls = MagicMock()
    paginator_instance = [{"id": 1}, {"id": 2}]
    paginator_cls.return_value = paginator_instance

    operation = ListOperation(
        path="/test", params={"q": "1"}, page_size=10, parse_func=dummy_parse_func
    )
    result = operation.execute_sync(client, paginator_cls)

    assert result == [{"id": 1}, {"id": 2}]
    paginator_cls.assert_called_once_with(client, "/test", params={"q": "1"}, page_size=10)


@pytest.mark.asyncio
async def test_list_operation_async():
    client = AsyncMock()
    paginator_cls = MagicMock()

    class AsyncIteratorMock:
        def __init__(self, items):
            self.items = items

        async def __aiter__(self):
            for item in self.items:
                yield item

    paginator_cls.return_value = AsyncIteratorMock([{"id": 1}, {"id": 2}])

    operation = ListOperation(
        path="/test", params={"q": "1"}, page_size=10, parse_func=dummy_parse_func
    )
    result = await operation.execute_async(client, paginator_cls)

    assert result == [{"id": 1}, {"id": 2}]
    paginator_cls.assert_called_once_with(client, "/test", params={"q": "1"}, page_size=10)


def test_filter_get_operation_sync():
    list_sync_func = MagicMock(return_value=[{"id": 1}])
    validate_func = MagicMock(return_value={"id": 1})
    client = MagicMock()
    paginator_cls = MagicMock()

    operation = FilterGetOperation(
        study_key="STUDY1",
        item_id=1,
        filters={"name": "test"},
        validate_func=validate_func,
        list_sync_func=list_sync_func,
    )

    result = operation.execute_sync(client, paginator_cls)

    assert result == {"id": 1}
    list_sync_func.assert_called_once_with(
        client, paginator_cls, study_key="STUDY1", refresh=True, name="test"
    )
    validate_func.assert_called_once_with([{"id": 1}], "STUDY1", 1)


def test_filter_get_operation_sync_missing_list_func():
    client = MagicMock()
    paginator_cls = MagicMock()

    operation = FilterGetOperation(
        study_key="STUDY1",
        item_id=1,
        filters={},
        validate_func=MagicMock(),
    )

    with pytest.raises(NotImplementedError, match="list_sync_func not provided"):
        operation.execute_sync(client, paginator_cls)


@pytest.mark.asyncio
async def test_filter_get_operation_async():
    list_async_func = AsyncMock(return_value=[{"id": 1}])
    validate_func = MagicMock(return_value={"id": 1})
    client = AsyncMock()
    paginator_cls = MagicMock()

    operation = FilterGetOperation(
        study_key="STUDY1",
        item_id=1,
        filters={"name": "test"},
        validate_func=validate_func,
        list_async_func=list_async_func,
    )

    result = await operation.execute_async(client, paginator_cls)

    assert result == {"id": 1}
    list_async_func.assert_called_once_with(
        client, paginator_cls, study_key="STUDY1", refresh=True, name="test"
    )
    validate_func.assert_called_once_with([{"id": 1}], "STUDY1", 1)


@pytest.mark.asyncio
async def test_filter_get_operation_async_missing_list_func():
    client = AsyncMock()
    paginator_cls = MagicMock()

    operation = FilterGetOperation(
        study_key="STUDY1",
        item_id=1,
        filters={},
        validate_func=MagicMock(),
    )

    with pytest.raises(NotImplementedError, match="list_async_func not provided"):
        await operation.execute_async(client, paginator_cls)


def test_record_create_operation_sync():
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"status": "created"}
    client.post.return_value = response

    operation = RecordCreateOperation(
        path="/create",
        records_data=[{"field1": "val1"}],
        email_notify=True,
    )

    result = operation.execute_sync(client, dummy_parse_func)

    assert result == {"status": "created"}
    client.post.assert_called_once_with(
        "/create", json=[{"field1": "val1"}], headers={HEADER_EMAIL_NOTIFY: "true"}
    )


def test_record_create_operation_header_validation_failure():
    with pytest.raises(ClientError, match="Header value must not contain newlines"):
        RecordCreateOperation(
            path="/create",
            records_data=[{"field1": "val1"}],
            email_notify="test@example.com\n",
        )


def test_record_create_operation_schema_validation_failure():
    schema_mock = MagicMock()

    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            "imednet.core.endpoint.operations.record_create.validate_record_entry",
            MagicMock(side_effect=ClientError("Invalid record data")),
        )

        with pytest.raises(ClientError, match="Invalid record data"):
            RecordCreateOperation(
                path="/create", records_data=[{"invalid": "data"}], schema=schema_mock
            )


@pytest.mark.asyncio
async def test_record_create_operation_async():
    client = AsyncMock()
    response = MagicMock()
    response.json.return_value = {"status": "created"}
    client.post.return_value = response

    operation = RecordCreateOperation(
        path="/create",
        records_data=[{"field1": "val1"}],
        email_notify="user@example.com",
    )

    result = await operation.execute_async(client, dummy_parse_func)

    assert result == {"status": "created"}
    client.post.assert_called_once_with(
        "/create", json=[{"field1": "val1"}], headers={HEADER_EMAIL_NOTIFY: "user@example.com"}
    )
