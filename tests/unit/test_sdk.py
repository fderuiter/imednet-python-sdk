from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.sdk import AsyncImednetSDK, ImednetSDK


@patch("imednet.sdk.ClientFactory")
def test_get_job_calls_jobs_endpoint(client_factory_mock):
    """Verify that the get_job method calls the get method on the jobs endpoint."""
    client_factory_mock.create.return_value = MagicMock(spec=Client)
    sdk = ImednetSDK(api_key="test", security_key="test")
    sdk.jobs = MagicMock()

    sdk.get_job("study1", "batch1")

    sdk.jobs.get.assert_called_once_with("study1", "batch1")


@pytest.mark.asyncio
@patch("imednet.sdk.ClientFactory")
async def test_async_get_job_calls_jobs_endpoint(client_factory_mock):
    """Verify that the async_get_job method calls the async_get method on the jobs endpoint."""
    client_factory_mock.create.side_effect = [
        MagicMock(spec=Client),
        MagicMock(spec=AsyncClient),
    ]
    sdk = AsyncImednetSDK(api_key="test", security_key="test")
    sdk.jobs = MagicMock()
    sdk.jobs.async_get = AsyncMock()

    await sdk.async_get_job("study1", "batch1")

    sdk.jobs.async_get.assert_called_once_with("study1", "batch1")


@patch("imednet.sdk.JobPoller")
@patch("imednet.sdk.ClientFactory")
def test_poll_job_uses_job_poller(client_factory_mock, job_poller_mock):
    """Verify that the poll_job method uses the JobPoller."""
    client_factory_mock.create.return_value = MagicMock(spec=Client)
    sdk = ImednetSDK(api_key="test", security_key="test")
    sdk.jobs = MagicMock()
    poller_instance = job_poller_mock.return_value

    sdk.poll_job("study1", "batch1", interval=10, timeout=100)

    job_poller_mock.assert_called_once_with(sdk.jobs.get, is_async=False)
    poller_instance.run.assert_called_once_with(
        "study1", "batch1", interval=10, timeout=100
    )


@pytest.mark.asyncio
@patch("imednet.sdk.JobPoller")
@patch("imednet.sdk.ClientFactory")
async def test_async_poll_job_uses_job_poller(client_factory_mock, job_poller_mock):
    """Verify that the async_poll_job method uses the JobPoller."""
    client_factory_mock.create.side_effect = [
        MagicMock(spec=Client),
        MagicMock(spec=AsyncClient),
    ]
    sdk = AsyncImednetSDK(api_key="test", security_key="test")
    sdk.jobs = MagicMock()
    sdk.jobs.async_get = AsyncMock()
    poller_instance = job_poller_mock.return_value
    poller_instance.run_async = AsyncMock()

    await sdk.async_poll_job("study1", "batch1", interval=10, timeout=100)

    job_poller_mock.assert_called_once_with(sdk.jobs.async_get, is_async=True)
    poller_instance.run_async.assert_called_once_with(
        "study1", "batch1", interval=10, timeout=100
    )
