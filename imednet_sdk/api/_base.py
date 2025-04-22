"""Base Class for API Resource Clients.

Defines the `ResourceClient`, the foundation for all specific API endpoint clients
(e.g., `StudiesClient`, `RecordsClient`). It provides common functionality and
delegates actual HTTP requests to the main `ImednetClient`.
"""

# Add necessary imports for type hints
from typing import (TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar,
                    Union)

# Import httpx for Response type hint if needed, or rely on client's type hints
import httpx
from pydantic import BaseModel

if TYPE_CHECKING:
    # Use forward reference to avoid circular import
    from imednet_sdk.client import ImednetClient, TimeoutTypes

# Define a TypeVar for generic response models used within resource clients
T = TypeVar("T", bound=BaseModel)


class ResourceClient:
    """Base class for specific iMednet API resource endpoint clients.

    Provides common helper methods (`_get`, `_post`, etc.) that wrap the core
    request logic of the main `ImednetClient`. Subclasses (e.g., `StudiesClient`)
    use these helpers to define methods corresponding to specific API operations
    (e.g., `list_studies`).

    This class should not be instantiated directly.

    Attributes:
        _client: The `ImednetClient` instance used for making HTTP requests.
    """

    def __init__(self, client: "ImednetClient"):
        """Initializes the resource client with a reference to the main client.

        Args:
            client: The `ImednetClient` instance that will execute the requests.
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
        """Sends a GET request via the main `ImednetClient`.

        This is a convenience method for subclasses to perform GET operations
        without directly accessing `_client._request`.

        Args:
            endpoint: The API endpoint path (relative to the base URL).
            params: Optional dictionary of query parameters.
            response_model: Optional Pydantic model class (or `List[ModelClass]`)
                            to parse the successful JSON response into.
            timeout: Optional timeout configuration override for this request.
            **kwargs: Additional keyword arguments passed to `ImednetClient._request`.

        Returns:
            The deserialized Pydantic model(s) or the raw `httpx.Response`,
            as returned by `ImednetClient._request`.

        Raises:
            Propagates exceptions raised by `ImednetClient._request` (e.g.,
            `ImednetSdkException` subclasses, `httpx.RequestError`).
        """
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
        """Sends a POST request via the main `ImednetClient`.

        This is a convenience method for subclasses to perform POST operations
        without directly accessing `_client._request`.

        Args:
            endpoint: The API endpoint path (relative to the base URL).
            json: Optional request body payload (dict, list, or Pydantic model).
            response_model: Optional Pydantic model class (or `List[ModelClass]`)
                            to parse the successful JSON response into.
            timeout: Optional timeout configuration override for this request.
            **kwargs: Additional keyword arguments passed to `ImednetClient._request`.

        Returns:
            The deserialized Pydantic model(s) or the raw `httpx.Response`,
            as returned by `ImednetClient._request`.

        Raises:
            Propagates exceptions raised by `ImednetClient._request` (e.g.,
            `ImednetSdkException` subclasses, `httpx.RequestError`).
        """
        return self._client._request(
            "POST", endpoint, json=json, response_model=response_model, timeout=timeout, **kwargs
        )

    # Add _put and _delete similarly if needed
    # def _put(...) -> ...:
    #     return self._client._request("PUT", ...)
    #
    # def _delete(...) -> ...:
    #     return self._client._request("DELETE", ...)
