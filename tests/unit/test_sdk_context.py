import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from imednet.sdk import ImednetSDK
from imednet.core.client import Client
from imednet.core.async_client import AsyncClient

# Mock environment variables to avoid API key requirement issues
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("IMEDNET_API_KEY", "test_api_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "test_sec_key")


def test_sync_context_manager():
    client_mock = MagicMock(spec=Client)

    with ImednetSDK(client=client_mock) as sdk:
        assert isinstance(sdk, ImednetSDK)

    client_mock.close.assert_called_once()


@pytest.mark.asyncio
async def test_async_context_manager():
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)
    async_client_mock.aclose = AsyncMock()

    async with ImednetSDK(client=client_mock, async_client=async_client_mock) as sdk:
        assert isinstance(sdk, ImednetSDK)

    client_mock.close.assert_called_once()
    async_client_mock.aclose.assert_awaited_once()


def test_close_without_running_loop():
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)

    # Use patch directly to avoid unawaited coroutines
    with patch("asyncio.get_running_loop", side_effect=RuntimeError("no running event loop")):
        with patch("asyncio.run") as mock_run:
            sdk = ImednetSDK(client=client_mock, async_client=async_client_mock)
            sdk.close()

            client_mock.close.assert_called_once()
            mock_run.assert_called_once()


def test_close_with_running_loop():
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)

    class MockLoop:
        def is_closed(self):
            return True

    with patch("asyncio.get_running_loop", return_value=MockLoop()):
        with patch("asyncio.run") as mock_run:
            sdk = ImednetSDK(client=client_mock, async_client=async_client_mock)
            sdk.close()

            client_mock.close.assert_called_once()
            mock_run.assert_called_once()


def test_close_with_running_loop_not_closed():
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)

    class MockLoop:
        def __init__(self):
            self.run_until_complete = MagicMock()

        def is_closed(self):
            return False

    mock_loop = MockLoop()

    with patch("asyncio.get_running_loop", return_value=mock_loop):
        sdk = ImednetSDK(client=client_mock, async_client=async_client_mock)
        sdk.close()

        client_mock.close.assert_called_once()
        mock_loop.run_until_complete.assert_called_once()


@pytest.mark.asyncio
async def test_aclose():
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)
    async_client_mock.aclose = AsyncMock()

    sdk = ImednetSDK(client=client_mock, async_client=async_client_mock)

    await sdk.aclose()

    client_mock.close.assert_called_once()
    async_client_mock.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_aclose_without_async_client():
    client_mock = MagicMock(spec=Client)

    sdk = ImednetSDK(client=client_mock)

    await sdk.aclose()

    client_mock.close.assert_called_once()


def test_study_methods():
    client_mock = MagicMock(spec=Client)
    sdk = ImednetSDK(client=client_mock)

    sdk.set_default_study("study-key-123")
    assert sdk.ctx.default_study_key == "study-key-123"

    sdk.clear_default_study()
    assert sdk.ctx.default_study_key is None


def test_retry_policy_property():
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)

    sdk = ImednetSDK(client=client_mock, async_client=async_client_mock)

    policy = MagicMock()

    # Test setter
    sdk.retry_policy = policy
    assert client_mock.retry_policy == policy
    assert async_client_mock.retry_policy == policy

    # Test getter
    client_mock.retry_policy = policy
    assert sdk.retry_policy == policy


def test_retry_policy_property_without_async_client():
    client_mock = MagicMock(spec=Client)
    sdk = ImednetSDK(client=client_mock)

    policy = MagicMock()

    # Test setter when async_client is None
    sdk.retry_policy = policy
    assert client_mock.retry_policy == policy


@pytest.mark.asyncio
async def test_async_sdk_aenter_aexit():
    from imednet.sdk import AsyncImednetSDK

    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)
    async_client_mock.aclose = AsyncMock()

    with patch("imednet.sdk.load_config"):
        with patch("imednet.sdk.ClientFactory.create_client", return_value=client_mock):
            with patch(
                "imednet.sdk.ClientFactory.create_async_client", return_value=async_client_mock
            ):
                async with AsyncImednetSDK() as sdk:
                    assert isinstance(sdk, AsyncImednetSDK)

                client_mock.close.assert_called_once()
                async_client_mock.aclose.assert_awaited_once()


def test_async_sdk_sync_init():
    from imednet.sdk import AsyncImednetSDK

    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)

    with patch("imednet.sdk.load_config"):
        with patch("imednet.sdk.ClientFactory.create_client", return_value=client_mock):
            with patch(
                "imednet.sdk.ClientFactory.create_async_client", return_value=async_client_mock
            ):
                sdk = AsyncImednetSDK()
                assert sdk._async_client == async_client_mock
