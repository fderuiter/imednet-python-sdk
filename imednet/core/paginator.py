"""Pagination helper for iterating through paginated API responses."""

from typing import Any, Dict, Iterator, Optional

import httpx


class _PaginatorBase:
    """Common initialization for pagination helpers."""

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
        self.client = client
        self.path = path
        self.params = params.copy() if params else {}
        self.page_size = page_size
        self.page_param = page_param
        self.size_param = size_param
        self.data_key = data_key
        self.metadata_key = metadata_key

    def _build_query(self, page: int) -> Dict[str, Any]:
        query = dict(self.params)
        query[self.page_param] = page
        query[self.size_param] = self.page_size
        return query


class Paginator(_PaginatorBase):
    """Iterate over pages of results from the iMednet API."""

    def __iter__(self) -> Iterator[Any]:
        page = 0
        while True:
            response: httpx.Response = self.client.get(self.path, params=self._build_query(page))
            payload = response.json()
            items = payload.get(self.data_key, []) or []
            for item in items:
                yield item
            # Use 'pagination' key instead of 'metadata' for pagination info
            pagination = payload.get("pagination", {})
            total_pages = pagination.get("totalPages")
            if total_pages is None or page >= total_pages - 1:
                break
            page += 1
