"""
Operation logic for getting single resources.

This module defines operations for retrieving individual items, either via
filtering a list (FilterGetOperation) or via a direct path (PathGetOperation).
"""

from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

from imednet.core.endpoint.protocols import (
    FilterGetEndpointProtocol,
    PathGetEndpointProtocol,
)
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class FilterGetOperation(Generic[T]):
    """
    Encapsulates execution logic for getting an item via filtering.

    This operation relies on the endpoint's list capability to find an item
    by its ID parameter.
    """

    def __init__(self, endpoint: FilterGetEndpointProtocol[T]) -> None:
        self.endpoint = endpoint

    def execute_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        """Execute synchronous get via filter."""
        filters = {self.endpoint._id_param: item_id}
        result = self.endpoint._list_sync(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )
        return self.endpoint._validate_get_result(result, study_key, item_id)

    async def execute_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        """Execute asynchronous get via filter."""
        filters = {self.endpoint._id_param: item_id}
        result = await self.endpoint._list_async(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )
        return self.endpoint._validate_get_result(result, study_key, item_id)


class PathGetOperation(Generic[T]):
    """
    Encapsulates execution logic for getting an item via direct path.

    This operation constructs a specific URL for the item ID and fetches it directly.
    """

    def __init__(self, endpoint: PathGetEndpointProtocol[T]) -> None:
        self.endpoint = endpoint

    def execute_sync(
        self,
        client: RequestorProtocol,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        """Execute synchronous get via path."""
        path = self.endpoint._get_path_for_id(study_key, item_id)
        response = client.get(path)
        return self.endpoint._process_response(response, study_key, item_id)

    async def execute_async(
        self,
        client: AsyncRequestorProtocol,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        """Execute asynchronous get via path."""
        path = self.endpoint._get_path_for_id(study_key, item_id)
        response = await client.get(path)
        return self.endpoint._process_response(response, study_key, item_id)
