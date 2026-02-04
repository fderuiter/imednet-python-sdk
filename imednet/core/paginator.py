"""Pagination helpers for iterating through API responses."""

from typing import Any, AsyncIterator, Dict, Iterator, Optional, cast

import httpx

from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol


class BasePaginator:
    """Shared paginator implementation."""

    def __init__(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_param: str = "page",
        size_param: str = "size",
        data_key: str = "data",
        metadata_key: str = "metadata",
    ) -> None:
        self.client = client
        self.path = path
        self.params = params.copy() if params else {}
        self.page_size = page_size
        self.page_param = page_param
        self.size_param = size_param
        self.data_key = data_key
        self.metadata_key = metadata_key

    def _build_params(self, page: int) -> Dict[str, Any]:
        query = dict(self.params)
        query[self.page_param] = page
        query[self.size_param] = self.page_size
        return query

    def _extract_items(self, payload: Dict[str, Any]) -> list[Any]:
        return payload.get(self.data_key, []) or []

    def _next_page(self, payload: Dict[str, Any], page: int) -> Optional[int]:
        pagination = payload.get("pagination", {})
        total_pages = pagination.get("totalPages")
        if total_pages is None or page >= total_pages - 1:
            return None
        return page + 1

    def _iter_sync(self) -> Iterator[Any]:
        client = cast(RequestorProtocol, self.client)
        page = 0
        while True:
            params = self._build_params(page)
            response: httpx.Response = client.get(self.path, params=params)
            payload = response.json()
            for item in self._extract_items(payload):
                yield item
            next_page = self._next_page(payload, page)
            if next_page is None:
                break
            page = next_page

    async def _iter_async(self) -> AsyncIterator[Any]:
        client = cast(AsyncRequestorProtocol, self.client)
        page = 0
        while True:
            params = self._build_params(page)
            response: httpx.Response = await client.get(self.path, params=params)
            payload = response.json()
            for item in self._extract_items(payload):
                yield item
            next_page = self._next_page(payload, page)
            if next_page is None:
                break
            page = next_page


class Paginator(BasePaginator):
    """Iterate synchronously over paginated API results."""

    def __iter__(self) -> Iterator[Any]:
        yield from self._iter_sync()


class AsyncPaginator(BasePaginator):
    """Asynchronous variant of :class:`Paginator`."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        async for item in self._iter_async():
            yield item


class BaseJsonListPaginator:
    """Paginator for APIs that return a single JSON list (no pagination)."""

    def __init__(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        **kwargs: Any,
    ) -> None:
        self.client = client
        self.path = path
        self.params = params or {}
        # page_size and kwargs are ignored but kept for signature compatibility


class JsonListPaginator(BaseJsonListPaginator):
    """Iterate synchronously over a JSON list response."""

    def __iter__(self) -> Iterator[Any]:
        client = cast(RequestorProtocol, self.client)
        response = client.get(self.path, params=self.params)
        items = response.json()
        if not isinstance(items, list):
            raise ValueError(f"Expected list response from {self.path}, got {type(items).__name__}")
        yield from items


class AsyncJsonListPaginator(BaseJsonListPaginator):
    """Iterate asynchronously over a JSON list response."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        client = cast(AsyncRequestorProtocol, self.client)
        response = await client.get(self.path, params=self.params)
        items = response.json()
        if not isinstance(items, list):
            raise ValueError(f"Expected list response from {self.path}, got {type(items).__name__}")
        for item in items:
            yield item
