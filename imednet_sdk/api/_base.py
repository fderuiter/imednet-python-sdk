"""Base class for API resource clients."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Use forward reference to avoid circular import
    from imednet_sdk.client import ImednetClient


class ResourceClient:
    """Base class for specific API resource clients."""

    def __init__(self, client: "ImednetClient"):
        """
        Initialize the resource client.

        Args:
            client: The main ImednetClient instance.
        """
        self._client = client
