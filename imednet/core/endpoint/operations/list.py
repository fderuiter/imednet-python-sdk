"""
Operation for listing resources.

Decouples the logic of iterating and parsing from the endpoint definition.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, List, TypeVar

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class ListOperation(Generic[T]):
    """
    Encapsulates the logic for listing resources.

    This class handles the iteration over paginated results and parsing of items.
    It is designed to be used via composition within endpoint implementations.
    """

    def execute_sync(
        self,
        paginator: Paginator,
        parse_func: Callable[[Any], T],
    ) -> List[T]:
        """
        Execute a synchronous list operation.

        Args:
            paginator: The paginator instance to iterate over.
            parse_func: A function to parse each raw item into a model.

        Returns:
            A list of parsed model instances.
        """
        return [parse_func(item) for item in paginator]

    async def execute_async(
        self,
        paginator: AsyncPaginator,
        parse_func: Callable[[Any], T],
    ) -> List[T]:
        """
        Execute an asynchronous list operation.

        Args:
            paginator: The async paginator instance to iterate over.
            parse_func: A function to parse each raw item into a model.

        Returns:
            A list of parsed model instances.
        """
        return [parse_func(item) async for item in paginator]
