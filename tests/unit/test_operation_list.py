"""TODO: Add docstring."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.core.endpoint.operations.list import ListOperation


def test_list_operation_sync_uses_paginator():
    """TODO: Add docstring."""
    client = MagicMock()
    paginator_cls = MagicMock(return_value=[{"id": 1}, {"id": 2}])

    operation = ListOperation(
        path="/records", params={"q": "x"}, page_size=50, parse_func=lambda x: x
    )
    result = list(operation.execute_sync(client, paginator_cls))

    assert result == [{"id": 1}, {"id": 2}]
    paginator_cls.assert_called_once_with(client, "/records", params={"q": "x"}, page_size=50)


@pytest.mark.asyncio
async def test_list_operation_async_uses_paginator():
    """TODO: Add docstring."""
    class _AsyncPaginator:
        """TODO: Add docstring."""
        def __init__(self, *_args, **_kwargs):
            """TODO: Add docstring."""
            pass

        async def __aiter__(self):
            """TODO: Add docstring."""
            for item in [{"id": 1}, {"id": 2}]:
                yield item

    paginator_cls = MagicMock(return_value=_AsyncPaginator())

    operation = ListOperation(path="/records", params={}, page_size=100, parse_func=lambda x: x)
    result = [item async for item in operation.execute_async(AsyncMock(), paginator_cls)]

    assert result == [{"id": 1}, {"id": 2}]
