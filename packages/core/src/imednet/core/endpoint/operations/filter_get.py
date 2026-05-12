"""
Operation for executing get requests via filtering.

This module encapsulates the logic for fetching a list of resources with a filter,
and then parsing and validating that a single item was found.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Generic, List, Optional, TypeVar

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

T = TypeVar("T")


class FilterGetOperation(Generic[T]):
    """
    Operation for executing get requests via filtering.

    Encapsulates the logic for making the list request, and validating
    that the target item exists in the result set.
    """

    def __init__(
        self,
        study_key: Optional[str],
        item_id: Any,
        filters: Dict[str, Any],
        validate_func: Callable[[List[T], Optional[str], Any], T],
        list_sync_func: Optional[Callable[..., List[T]]] = None,
        list_async_func: Optional[Callable[..., Awaitable[List[T]]]] = None,
    ) -> None:
        """
        Initialize the filter get operation.

        Args:
            study_key: The study key.
            item_id: The ID of the item to fetch.
            filters: The filters to apply.
            validate_func: A function to validate and extract the result.
            list_sync_func: The synchronous list function.
            list_async_func: The asynchronous list function.
        """
        self.study_key = study_key
        self.item_id = item_id
        self.filters = filters
        self.validate_func = validate_func
        self.list_sync_func = list_sync_func
        self.list_async_func = list_async_func

    def execute_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
    ) -> T:
        """
        Execute synchronous get request.

        Args:
            client: The synchronous HTTP client.
            paginator_cls: The paginator class to use.

        Returns:
            The parsed item.
        """
        if self.list_sync_func is None:
            raise NotImplementedError("list_sync_func not provided")

        result = self.list_sync_func(
            client,
            paginator_cls,
            study_key=self.study_key,
            refresh=True,
            **self.filters,
        )
        return self.validate_func(result, self.study_key, self.item_id)

    async def execute_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
    ) -> T:
        """
        Execute asynchronous get request.

        Args:
            client: The asynchronous HTTP client.
            paginator_cls: The async paginator class to use.

        Returns:
            The parsed item.
        """
        if self.list_async_func is None:
            raise NotImplementedError("list_async_func not provided")

        result = await self.list_async_func(
            client,
            paginator_cls,
            study_key=self.study_key,
            refresh=True,
            **self.filters,
        )
        return self.validate_func(result, self.study_key, self.item_id)
