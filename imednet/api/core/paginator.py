"""Pagination helpers for iterating through API responses."""

from typing import Any, AsyncIterator, Dict, Iterator, Optional

import httpx


class BasePaginator:
    """Shared paginator implementation."""

    def __init__(
        self,
        client: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_param: str = "page",
        size_param: str = "size",
        data_key: str = "data",
        metadata_key: str = "metadata",
    ) -> None:
        """Initializes the BasePaginator.

        Args:
            client: The HTTP client to use for requests.
            path: The API endpoint path.
            params: Query parameters to include in the request.
            page_size: The number of items to request per page.
            page_param: The name of the page query parameter.
            size_param: The name of the page size query parameter.
            data_key: The key in the response payload that contains the data.
            metadata_key: The key in the response payload that contains metadata.
        """
        self.client = client
        self.path = path
        self.params = params.copy() if params else {}
        self.page_size = page_size
        self.page_param = page_param
        self.size_param = size_param
        self.data_key = data_key
        self.metadata_key = metadata_key

    def _build_params(self, page: int) -> Dict[str, Any]:
        """Build the query parameters for a specific page.

        Args:
            page: The page number to request.

        Returns:
            A dictionary of query parameters.
        """
        query = dict(self.params)
        query[self.page_param] = page
        query[self.size_param] = self.page_size
        return query

    def _extract_items(self, payload: Dict[str, Any]) -> list[Any]:
        """Extract the list of items from the response payload.

        Args:
            payload: The response payload.

        Returns:
            A list of items.
        """
        return payload.get(self.data_key, []) or []

    def _next_page(self, payload: Dict[str, Any], page: int) -> Optional[int]:
        """Determine the next page number from the response payload.

        Args:
            payload: The response payload.
            page: The current page number.

        Returns:
            The next page number, or None if there are no more pages.
        """
        pagination = payload.get("pagination", {})
        total_pages = pagination.get("totalPages")
        if total_pages is None or page >= total_pages - 1:
            return None
        return page + 1

    def _iter_sync(self) -> Iterator[Any]:
        """Iterate synchronously over all pages and yield items.

        Yields:
            Items from the paginated response.
        """
        page = 0
        while True:
            params = self._build_params(page)
            response: httpx.Response = self.client.get(self.path, params=params)
            payload = response.json()
            for item in self._extract_items(payload):
                yield item
            next_page = self._next_page(payload, page)
            if next_page is None:
                break
            page = next_page

    async def _iter_async(self) -> AsyncIterator[Any]:
        """Iterate asynchronously over all pages and yield items.

        Yields:
            Items from the paginated response.
        """
        page = 0
        while True:
            params = self._build_params(page)
            response: httpx.Response = await self.client.get(self.path, params=params)
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
        """Start the synchronous iteration.

        Yields:
            Items from the paginated response.
        """
        yield from self._iter_sync()


class AsyncPaginator(BasePaginator):
    """Asynchronous variant of :class:`Paginator`."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        """Start the asynchronous iteration.

        Yields:
            Items from the paginated response.
        """
        async for item in self._iter_async():
            yield item
