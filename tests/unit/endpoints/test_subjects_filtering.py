"""TODO: Add docstring."""

from unittest.mock import AsyncMock, Mock

import pytest

from imednet.endpoints.subjects import AsyncSubjectsEndpoint, SubjectsEndpoint


def test_list_by_site_filtering():
    """TODO: Add docstring."""
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
    """TODO: Add docstring."""
    mock_client = Mock()
    mock_ctx = Mock()

    endpoint = AsyncSubjectsEndpoint(mock_client, mock_ctx)

    async def fake_async_list(*args, **kwargs):
        """TODO: Add docstring."""
        if False:
            yield

    endpoint.list = Mock(return_value=fake_async_list())

    await endpoint.async_list_by_site("sk", 101)
    endpoint.list.assert_called_with(study_key="sk", site_id=101)

    endpoint.list = Mock(return_value=fake_async_list())
    await endpoint.async_list_by_site("sk", "101")
    endpoint.list.assert_called_with(study_key="sk", site_id="101")
