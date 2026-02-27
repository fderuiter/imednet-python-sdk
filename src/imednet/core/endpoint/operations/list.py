"""
Operation for executing list requests.

This module encapsulates the logic for fetching and parsing a list of resources
from the API, handling pagination seamlessly.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Generic, List, TypeVar

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

T = TypeVar("T")


class ListOperation(Generic[T]):
    """
    Operation for executing list requests.

    Encapsulates the logic for setting up a paginator, iterating through pages,
    and parsing the results.
    """

    def __init__(
        self,
        path: str,
        params: Dict[str, Any],
        page_size: int,
        parse_func: Callable[[Any], T],
    ) -> None:
        """
        Initialize the list operation.

        Args:
            path: The API endpoint path.
            params: Query parameters for the request.
            page_size: The number of items per page.
            parse_func: A function to parse a raw JSON item into the model T.
        """
        self.path = path
        self.params = params
        self.page_size = page_size
        self.parse_func = parse_func

    def execute_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
    ) -> List[T]:
        """
        Execute synchronous list request.

        Args:
            client: The synchronous HTTP client.
            paginator_cls: The paginator class to use.

        Returns:
            A list of parsed items.
        """
        paginator = paginator_cls(
            client,
            self.path,
            params=self.params,
            page_size=self.page_size,
        )
        return [self.parse_func(item) for item in paginator]

    async def execute_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
    ) -> List[T]:
        """
        Execute asynchronous list request.

        Args:
            client: The asynchronous HTTP client.
            paginator_cls: The async paginator class to use.

        Returns:
            A list of parsed items.
        """
        paginator = paginator_cls(
            client,
            self.path,
            params=self.params,
            page_size=self.page_size,
        )
        return [self.parse_func(item) async for item in paginator]
