"""Tests for core protocols."""

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol


def test_client_implements_protocol():
    # We can't check isinstance easily without instantiating, or use runtime_checkable
    # Since I added @runtime_checkable, it should work.

    # However, to be safe and avoid instantiation side effects (like load_config),
    # let's just assume if it runs it's fine, but better to check method existence?
    # No, runtime_checkable checks method existence.

    assert issubclass(Client, RequestorProtocol)


def test_async_client_implements_protocol():
    assert issubclass(AsyncClient, AsyncRequestorProtocol)
