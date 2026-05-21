"""Pagination helpers for iterating through API responses."""

from typing import Any, AsyncIterator, Dict, Generic, Iterator, Optional, TypeVar

import httpx

from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.errors.client import PaginationError

ClientT = TypeVar("ClientT", RequestorProtocol, AsyncRequestorProtocol)


class BasePaginator(Generic[ClientT]):
    """Shared paginator implementation."""

    def __init__(
        self,
        client: ClientT,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_param: str = "page",
        size_param: str = "size",
        data_key: str = "data",
        metadata_key: str = "metadata",
    ) -> None:
        self.client: ClientT = client
        self.path = path
        self.params = params.copy() if params else {}
        self.page_size = page_size
        self.page_param = page_param
        self.size_param = size_param
        self.data_key = data_key
        self.metadata_key = metadata_key
        self._cursor: Optional[int] = 0

    @property
    def cursor(self) -> Optional[int]:
        """The next page cursor (0-based page index), or ``None`` when exhausted."""
        return self._cursor

    def _build_params(self, page: int) -> Dict[str, Any]:
        query = dict(self.params)
        query[self.page_param] = page
        query[self.size_param] = self.page_size
        return query

    def _extract_items(self, payload: Dict[str, Any]) -> list[Any]:
        if not isinstance(payload, dict):
            raise TypeError(f"API response must be a dictionary, got {type(payload).__name__}")
        items = payload.get(self.data_key, []) or []
        if not isinstance(items, list):
            raise TypeError(
                f"Expected a list of items under key '{self.data_key}', got {type(items).__name__}"
            )
        return items

    def _next_page(self, payload: Dict[str, Any], page: int, items_count: int) -> Optional[int]:
        pagination = payload.get("pagination")
        if pagination is not None and not isinstance(pagination, dict):
            raise TypeError(
                f"Response field 'pagination' must be a dictionary, got {type(pagination).__name__}"
            )
        pagination = pagination or {}
        total_pages = pagination.get("totalPages")
        if total_pages is None:
            if items_count >= self.page_size:
                raise PaginationError(
                    "Response pagination metadata is missing required 'totalPages' cursor."
                )
            return None
        if not isinstance(total_pages, int) or isinstance(total_pages, bool):
            raise PaginationError(
                "Response pagination cursor 'totalPages' must be an integer, "
                f"got {type(total_pages).__name__}."
            )
        if total_pages < 0:
            raise PaginationError("Response pagination cursor 'totalPages' cannot be negative.")
        if total_pages == 0:
            if items_count > 0:
                raise PaginationError(
                    "Response pagination cursor 'totalPages' cannot be 0 when items are present."
                )
            return None
        if page >= total_pages:
            raise PaginationError(
                "Response pagination cursor 'totalPages' is inconsistent with the current page."
            )
        if page >= total_pages - 1:
            return None
        return page + 1


class Paginator(BasePaginator[RequestorProtocol]):
    """Iterate synchronously over paginated API results."""

    def __iter__(self) -> Iterator[Any]:
        page = 0
        self._cursor = page
        while True:
            params = self._build_params(page)
            response: httpx.Response = self.client.get(self.path, params=params)
            payload = response.json()
            items = self._extract_items(payload)
            for item in items:
                yield item
            next_page = self._next_page(payload, page, len(items))
            self._cursor = next_page
            if next_page is None:
                break
            page = next_page


class AsyncPaginator(BasePaginator[AsyncRequestorProtocol]):
    """Asynchronous variant of :class:`Paginator`."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        page = 0
        self._cursor = page
        while True:
            params = self._build_params(page)
            response: httpx.Response = await self.client.get(self.path, params=params)
            payload = response.json()
            items = self._extract_items(payload)
            for item in items:
                yield item
            next_page = self._next_page(payload, page, len(items))
            self._cursor = next_page
            if next_page is None:
                break
            page = next_page


class JsonListPaginator(Paginator):
    """Paginator for endpoints returning a raw list."""

    def __iter__(self) -> Iterator[Any]:
        # Raw list endpoints do not support pagination params
        response: httpx.Response = self.client.get(self.path, params=self.params)
        payload = response.json()
        if not isinstance(payload, list):
            raise TypeError(f"API response must be a list, got {type(payload).__name__}")
        yield from payload


class AsyncJsonListPaginator(AsyncPaginator):
    """Asynchronous variant of :class:`JsonListPaginator`."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        # Raw list endpoints do not support pagination params
        response: httpx.Response = await self.client.get(self.path, params=self.params)
        payload = response.json()
        if not isinstance(payload, list):
            raise TypeError(f"API response must be a list, got {type(payload).__name__}")
        for item in payload:
            yield item
