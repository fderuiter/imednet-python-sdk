from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.sdk import AsyncImednetSDK, ImednetSDK


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

    with patch("imednet.sdk.ClientFactory.create_client", return_value=client_mock):
        with patch("imednet.sdk.ClientFactory.create_async_client", return_value=async_client_mock):
            async with AsyncImednetSDK() as sdk:
                assert isinstance(sdk, AsyncImednetSDK)

    client_mock.close.assert_called_once()
    async_client_mock.aclose.assert_awaited_once()


def test_close_without_async_client():
    client_mock = MagicMock(spec=Client)
    sdk = ImednetSDK(client=client_mock)
    sdk.close()
    client_mock.close.assert_called_once()


def test_close_with_async_client_raises_runtime_error():
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)

    sdk = ImednetSDK(client=client_mock, async_client=async_client_mock)

    with pytest.raises(RuntimeError, match="await sdk.aclose"):
        sdk.close()

    client_mock.close.assert_not_called()


def test_async_sdk_close_raises_type_error():
    """AsyncImednetSDK.close() raises TypeError — sync close is forbidden."""
    with patch("imednet.sdk.load_config"):
        with patch("imednet.sdk.ClientFactory.create_client", return_value=MagicMock(spec=Client)):
            with patch(
                "imednet.sdk.ClientFactory.create_async_client",
                return_value=MagicMock(spec=AsyncClient),
            ):
                sdk = AsyncImednetSDK()
                with pytest.raises(TypeError, match="await sdk.aclose"):
                    sdk.close()


def test_async_sdk_sync_context_manager_raises_type_error():
    with patch("imednet.sdk.load_config"):
        with patch("imednet.sdk.ClientFactory.create_client", return_value=MagicMock(spec=Client)):
            with patch(
                "imednet.sdk.ClientFactory.create_async_client",
                return_value=MagicMock(spec=AsyncClient),
            ):
                sdk = AsyncImednetSDK()
                with pytest.raises(TypeError, match="async with AsyncImednetSDK"):
                    with sdk:
                        pass  # pragma: no cover


def test_async_sdk_exit_raises_type_error():
    """__exit__ on AsyncImednetSDK raises TypeError when called directly."""
    with patch("imednet.sdk.load_config"):
        with patch("imednet.sdk.ClientFactory.create_client", return_value=MagicMock(spec=Client)):
            with patch(
                "imednet.sdk.ClientFactory.create_async_client",
                return_value=MagicMock(spec=AsyncClient),
            ):
                sdk = AsyncImednetSDK()
                with pytest.raises(TypeError, match="async with AsyncImednetSDK"):
                    sdk.__exit__(None, None, None)


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
    client_mock = MagicMock(spec=Client)
    async_client_mock = MagicMock(spec=AsyncClient)

    with patch("imednet.sdk.load_config"):
        with patch("imednet.sdk.ClientFactory.create_client", return_value=client_mock):
            with patch(
                "imednet.sdk.ClientFactory.create_async_client", return_value=async_client_mock
            ):
                sdk = AsyncImednetSDK()
                assert sdk._async_client == async_client_mock


@pytest.mark.asyncio
async def test_sync_sdk_rejects_async_context():
    """ImednetSDK.__aenter__ raises TypeError — async with is forbidden."""
    client_mock = MagicMock(spec=Client)
    sdk = ImednetSDK(client=client_mock)
    with pytest.raises(TypeError, match="synchronous client"):
        await sdk.__aenter__()


@pytest.mark.asyncio
async def test_sync_sdk_rejects_async_context_via_async_with():
    """'async with ImednetSDK(...)' raises TypeError before entering the block."""
    client_mock = MagicMock(spec=Client)
    sdk = ImednetSDK(client=client_mock)
    with pytest.raises(TypeError, match="synchronous client"):
        async with sdk:
            pass  # pragma: no cover
