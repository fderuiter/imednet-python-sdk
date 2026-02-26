"""
Operation logic for listing resources.

This module defines the ListOperation class, which encapsulates the execution
logic for synchronous and asynchronous list operations, separating it from
the endpoint configuration.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, List, Optional, TypeVar

from imednet.core.endpoint.protocols import ListEndpointProtocol
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class ListOperation(Generic[T]):
    """
    Encapsulates execution logic for list operations.

    Handles iteration over paginated results and parsing of items,
    delegating state management and result processing back to the endpoint.
    """

    def __init__(self, endpoint: ListEndpointProtocol[T]) -> None:
        self.endpoint = endpoint

    def execute_sync(
        self,
        paginator: Paginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        """
        Execute synchronous list retrieval.

        Args:
            paginator: The paginator to iterate over.
            parse_func: The function to parse raw items into models.
            study: The study context.
            has_filters: Whether filters were applied.
            cache: The cache object.

        Returns:
            The list of parsed items.
        """
        # Execute iteration
        result = [parse_func(item) for item in paginator]

        # Process result (update cache, etc.)
        return self.endpoint._process_list_result(result, study, has_filters, cache)

    async def execute_async(
        self,
        paginator: AsyncPaginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        """
        Execute asynchronous list retrieval.

        Args:
            paginator: The async paginator to iterate over.
            parse_func: The function to parse raw items into models.
            study: The study context.
            has_filters: Whether filters were applied.
            cache: The cache object.

        Returns:
            The list of parsed items.
        """
        # Execute iteration
        result = [parse_func(item) async for item in paginator]

        # Process result (update cache, etc.)
        return self.endpoint._process_list_result(result, study, has_filters, cache)
