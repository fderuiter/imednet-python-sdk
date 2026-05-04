from unittest.mock import AsyncMock, Mock

import pytest

from imednet.endpoints.subjects import SubjectsEndpoint


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

    endpoint = SubjectsEndpoint(mock_client, mock_ctx)
    endpoint.async_list = AsyncMock(return_value=[])

    await endpoint.async_list_by_site("sk", 101)
    endpoint.async_list.assert_called_with(study_key="sk", site_id=101)

    await endpoint.async_list_by_site("sk", "101")
    endpoint.async_list.assert_called_with(study_key="sk", site_id="101")
