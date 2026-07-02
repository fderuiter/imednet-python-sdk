"""Pagination helpers for iterating through API responses."""

from typing import Any, AsyncIterator, Dict, Generic, Iterator, Optional, TypeVar

import httpx

from imednet.core.protocols import AsyncRequesterProtocol, RequesterProtocol
from imednet.errors.client import PaginationError

ClientT = TypeVar("ClientT", RequesterProtocol, AsyncRequesterProtocol)


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
        """Initialize the paginator.

        Args:
            client: Requester instance (sync or async).
            path: API path for the request.
            params: Query parameters.
            page_size: Number of items per page.
            page_param: Query parameter name for the page index.
            size_param: Query parameter name for the page size.
            data_key: Key in the response JSON containing the items list.
            metadata_key: Key in the response JSON containing pagination metadata.
        """
        self.client: ClientT = client
        self.path = path
        self.params = params.copy() if params else {}
        self.page_size = page_size
        self.page_param = page_param
        self.size_param = size_param
        self.data_key = data_key
        self.metadata_key = metadata_key
        self._cursor: Optional[int] = None

    @property
    def cursor(self) -> Optional[int]:
        """The next page cursor (0-based page index), or ``None`` when exhausted."""
        return self._cursor

    def _build_params(self, page: int) -> Dict[str, Any]:
        """Build the query parameters for a specific page."""
        query = dict(self.params)
        query[self.page_param] = page
        query[self.size_param] = self.page_size
        return query

    def _extract_items(self, payload: Dict[str, Any]) -> list[Any]:
        """Extract item list from the API response payload."""
        if not isinstance(payload, dict):
            raise TypeError(f"API response must be a dictionary, got {type(payload).__name__}")

        if "recordData" in payload:
            items = payload.get("recordData", []) or []
        else:
            items = payload.get(self.data_key, []) or []

        if not isinstance(items, list):
            raise TypeError(
                f"Expected a list of items under key '{self.data_key}', got {type(items).__name__}"
            )
        return items

    def _next_page(self, payload: Dict[str, Any], page: int, items_count: int) -> Optional[int]:
        """Determine the next page index based on the response payload and metadata."""
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
        if isinstance(total_pages, bool) or not isinstance(total_pages, int):
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

    def _get_page_params(self) -> Optional[Dict[str, Any]]:
        """Return parameters for the current page or None if exhausted."""
        if self._cursor is None:
            return None
        return self._build_params(self._cursor)

    def _process_page_response(self, payload: Dict[str, Any]) -> list[Any]:
        """Process payload, update cursor, and return items."""
        if self._cursor is None:
            return []
        items = self._extract_items(payload)
        self._cursor = self._next_page(payload, self._cursor, len(items))
        return items

    def _process_json_list_response(self, payload: Any) -> list[Any]:
        """Process raw list response."""
        if not isinstance(payload, list):
            raise TypeError(f"API response must be a list, got {type(payload).__name__}")
        return payload


class Paginator(BasePaginator[RequesterProtocol]):
    """Iterate synchronously over paginated API results."""

    def __iter__(self) -> Iterator[Any]:
        """Iterate over all items across all pages."""
        from imednet.core.operations.executor import UniversalExecutor

        retries = getattr(self.client, "retries", 3)
        backoff_factor = getattr(self.client, "backoff_factor", 1.0)
        tracer = getattr(self.client, "_tracer", None)

        attributes: Dict[str, Any] = {"path": self.path}
        if self.params:
            for k, v in self.params.items():
                attributes[k] = v

        executor = UniversalExecutor(
            retries=retries,
            backoff_factor=backoff_factor,
            tracer=tracer,
            operation_name="list_page",
            **attributes,
        )

        self._cursor = 0
        while self._cursor is not None:
            params = self._get_page_params()

            def _fetch() -> httpx.Response:
                return self.client.get(self.path, params=params)

            response: httpx.Response = executor.execute(_fetch)
            payload = response.json()
            items = self._process_page_response(payload)
            yield from items


class AsyncPaginator(BasePaginator[AsyncRequesterProtocol]):
    """Asynchronous variant of :class:`Paginator`."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        """Iterate asynchronously over all items across all pages."""
        from imednet.core.operations.executor import UniversalExecutor

        retries = getattr(self.client, "retries", 3)
        backoff_factor = getattr(self.client, "backoff_factor", 1.0)
        tracer = getattr(self.client, "_tracer", None)

        attributes: Dict[str, Any] = {"path": self.path}
        if self.params:
            for k, v in self.params.items():
                attributes[k] = v

        executor = UniversalExecutor(
            retries=retries,
            backoff_factor=backoff_factor,
            tracer=tracer,
            operation_name="list_page",
            **attributes,
        )

        self._cursor = 0
        while self._cursor is not None:
            params = self._get_page_params()

            async def _fetch() -> httpx.Response:
                return await self.client.get(self.path, params=params)

            response: httpx.Response = await executor.execute_async(_fetch)
            payload = response.json()
            items = self._process_page_response(payload)
            for item in items:
                yield item


class JsonListPaginator(Paginator):
    """Paginator for endpoints returning a raw list."""

    def __iter__(self) -> Iterator[Any]:
        """Iterate over a single response that returns a list directly."""
        from imednet.core.operations.executor import UniversalExecutor

        retries = getattr(self.client, "retries", 3)
        backoff_factor = getattr(self.client, "backoff_factor", 1.0)
        tracer = getattr(self.client, "_tracer", None)

        attributes: Dict[str, Any] = {"path": self.path}
        if self.params:
            for k, v in self.params.items():
                attributes[k] = v

        executor = UniversalExecutor(
            retries=retries,
            backoff_factor=backoff_factor,
            tracer=tracer,
            operation_name="list_page",
            **attributes,
        )

        def _fetch() -> httpx.Response:
            return self.client.get(self.path, params=self.params)

        response: httpx.Response = executor.execute(_fetch)
        payload = response.json()
        yield from self._process_json_list_response(payload)


class AsyncJsonListPaginator(AsyncPaginator):
    """Asynchronous variant of :class:`JsonListPaginator`."""

    async def __aiter__(self) -> AsyncIterator[Any]:
        """Iterate asynchronously over a single response that returns a list directly."""
        from imednet.core.operations.executor import UniversalExecutor

        retries = getattr(self.client, "retries", 3)
        backoff_factor = getattr(self.client, "backoff_factor", 1.0)
        tracer = getattr(self.client, "_tracer", None)

        attributes: Dict[str, Any] = {"path": self.path}
        if self.params:
            for k, v in self.params.items():
                attributes[k] = v

        executor = UniversalExecutor(
            retries=retries,
            backoff_factor=backoff_factor,
            tracer=tracer,
            operation_name="list_page",
            **attributes,
        )

        async def _fetch() -> httpx.Response:
            return await self.client.get(self.path, params=self.params)

        response: httpx.Response = await executor.execute_async(_fetch)
        payload = response.json()
        for item in self._process_json_list_response(payload):
            yield item
