"""
Pagination helper for iterating through paginated API responses.
"""

from typing import Any, Dict, Iterator, Optional

import httpx


class Paginator:
    """
    Iterate over pages of results from the iMednet API.

    Example:
        paginator = Paginator(client, "/api/v1/edc/studies/{study_key}/sites")
        for item in paginator:
            # process each item
    """

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
    ):
        self.client = client
        self.path = path
        self.params = params.copy() if params else {}
        self.page_size = page_size
        self.page_param = page_param
        self.size_param = size_param
        self.data_key = data_key
        self.metadata_key = metadata_key

    def __iter__(self) -> Iterator[Any]:
        page = 0
        while True:
            query = dict(self.params)
            query[self.page_param] = page
            query[self.size_param] = self.page_size
            response: httpx.Response = self.client.get(self.path, params=query)
            payload = response.json()
            items = payload.get(self.data_key, []) or []
            for item in items:
                yield item
            metadata = payload.get(self.metadata_key, {})
            total_pages = metadata.get("totalPages")
            if total_pages is None or page >= total_pages - 1:
                break
            page += 1
