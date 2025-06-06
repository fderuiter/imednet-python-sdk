"""Asynchronous pagination helper for iMednet API."""

from typing import Any, AsyncIterator, Dict, Optional

import httpx

from .paginator import _PaginatorBase


class AsyncPaginator(_PaginatorBase):
    """Iterate over pages of results asynchronously."""

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
        super().__init__(
            client,
            path,
            params=params,
            page_size=page_size,
            page_param=page_param,
            size_param=size_param,
            data_key=data_key,
            metadata_key=metadata_key,
        )

    async def __aiter__(self) -> AsyncIterator[Any]:
        page = 0
        while True:
            response: httpx.Response = await self.client.get(
                self.path, params=self._build_query(page)
            )
            payload = response.json()
            items = payload.get(self.data_key, []) or []
            for item in items:
                yield item
            pagination = payload.get("pagination", {})
            total_pages = pagination.get("totalPages")
            if total_pages is None or page >= total_pages - 1:
                break
            page += 1
