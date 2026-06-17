from unittest.mock import AsyncMock, Mock

import pytest

from imednet.endpoints.subjects import AsyncSubjectsEndpoint, SubjectsEndpoint


def test_list_by_site_filtering():
    mock_client = Mock()
    mock_ctx = Mock()

    endpoint = SubjectsEndpoint(mock_client, mock_ctx)
    endpoint.list = Mock(return_value=[])

    endpoint.list_by_site("sk", 101)
    endpoint.list.assert_called_with(study_key="sk", site_id=101)

    endpoint.list_by_site("sk", "101")
    endpoint.list.assert_called_with(study_key="sk", site_id="101")


@pytest.mark.asyncio
async def test_async_list_by_site_filtering():
    mock_client = Mock()
    mock_ctx = Mock()

    endpoint = AsyncSubjectsEndpoint(mock_client, mock_ctx)
    class MockAsyncGenerator:
        async def __aiter__(self):
            for item in []:
                yield item
                
    mock_async_list = Mock()
    mock_async_list.return_value = MockAsyncGenerator()
    endpoint.async_list = mock_async_list

    await endpoint.async_list_by_site("sk", 101)
    endpoint.async_list.assert_called_with(study_key="sk", site_id=101)

    await endpoint.async_list_by_site("sk", "101")
    endpoint.async_list.assert_called_with(study_key="sk", site_id="101")
