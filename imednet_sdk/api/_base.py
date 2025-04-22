"""Base class for API resource clients."""

# Add necessary imports for type hints
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union

# Import httpx for Response type hint if needed, or rely on client's type hints
import httpx
from pydantic import BaseModel

if TYPE_CHECKING:
    # Use forward reference to avoid circular import
    from imednet_sdk.client import ImednetClient, TimeoutTypes

# Define a TypeVar for generic response models used within resource clients
T = TypeVar("T", bound=BaseModel)


class ResourceClient:
    """Base class for specific API resource clients.

    Provides helper methods for making common HTTP requests (GET, POST, PUT, DELETE)
    by delegating to the main ImednetClient instance.
    """

    def __init__(self, client: "ImednetClient"):
        """
        Initializes the resource client, storing a reference to the main ImednetClient.

        Args:
            client: The main ImednetClient instance.
        """
        self._client = client

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: "Optional[TimeoutTypes]" = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Sends a GET request via the main client."""
        return self._client._request(
            "GET", endpoint, params=params, response_model=response_model, timeout=timeout, **kwargs
        )

    def _post(
        self,
        endpoint: str,
        json: Optional[Any] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: "Optional[TimeoutTypes]" = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Sends a POST request via the main client."""
        return self._client._request(
            "POST", endpoint, json=json, response_model=response_model, timeout=timeout, **kwargs
        )

    # Add _put and _delete similarly if needed
    # def _put(...) -> ...:
    #     return self._client._request("PUT", ...)
    #
    # def _delete(...) -> ...:
    #     return self._client._request("DELETE", ...)
