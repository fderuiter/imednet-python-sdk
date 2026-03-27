from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.core.endpoint.operations.get import PathGetOperation


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

    not_found_func = MagicMock(side_effect=ValueError("Not found"))

    operation = PathGetOperation(
        path="/test", parse_func=dummy_parse_func, not_found_func=not_found_func
    )

    with pytest.raises(ValueError, match="Not found"):
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

    not_found_func = MagicMock(side_effect=ValueError("Not found"))

    operation = PathGetOperation(
        path="/test", parse_func=dummy_parse_func, not_found_func=not_found_func
    )

    with pytest.raises(ValueError, match="Not found"):
        await operation.execute_async(client)

    client.get.assert_called_once_with("/test")
    not_found_func.assert_called_once()
