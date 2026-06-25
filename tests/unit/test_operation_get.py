"""Test Operation Get module."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.core.endpoint.operations.filter_get import FilterGetOperation
from imednet.core.endpoint.operations.get import PathGetOperation
from imednet.errors import NotFoundError


def test_filter_get_operation_returns_first_result():
    """Test the test filter get operation returns first result functionality."""
    validate = MagicMock(return_value={"id": 123})
    list_sync = MagicMock(return_value=[{"id": 123}])

    operation = FilterGetOperation(
        study_key="STUDY",
        item_id=123,
        filters={"id": 123},
        validate_func=validate,
        list_sync_func=list_sync,
    )

    result = operation.execute_sync(MagicMock(), MagicMock())

    assert result == {"id": 123}
    list_sync.assert_called_once()
    validate.assert_called_once_with([{"id": 123}], "STUDY", 123)


@pytest.mark.asyncio
async def test_filter_get_operation_async_missing_callable():
    """Implementation detail."""
    operation = FilterGetOperation(
        study_key="STUDY",
        item_id=123,
        filters={"id": 123},
        validate_func=MagicMock(),
    )

    with pytest.raises(NotImplementedError, match="list_async_func not provided"):
        await operation.execute_async(AsyncMock(), MagicMock())


def test_path_get_operation_not_found_callback():
    """Test the test path get operation not found callback functionality."""
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = None
    client.get.return_value = response

    def raise_not_found() -> None:
        """Test the raise not found functionality."""
        raise NotFoundError("missing")

    operation = PathGetOperation(
        path="/studies/S1/jobs/123",
        parse_func=lambda data: data,
        not_found_func=raise_not_found,
    )

    with pytest.raises(NotFoundError, match="missing"):
        operation.execute_sync(client)


def test_path_get_operation_calls_parse_func():
    """Test the test path get operation calls parse func functionality."""
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"jobId": "1"}
    client.get.return_value = response
    parse = MagicMock(return_value={"job_id": "1"})

    operation = PathGetOperation(
        path="/studies/S1/jobs/123",
        parse_func=parse,
        not_found_func=MagicMock(),
    )

    result = operation.execute_sync(client)

    assert result == {"job_id": "1"}
    parse.assert_called_once_with({"jobId": "1"})
