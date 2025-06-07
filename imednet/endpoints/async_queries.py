"""Async endpoint for managing queries in a study."""

from typing import Any, List, Optional, cast

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.queries import Query


class AsyncQueriesEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with queries."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Query]:
        paginator = cast(
            AsyncPaginator,
            build_paginator(
                self,
                AsyncPaginator,
                "queries",
                study_key,
                page_size,
                filters,
            ),
        )
        return [Query.from_json(item) async for item in paginator]

    async def get(self, study_key: str, annotation_id: int) -> Query:
        path = self._build_path(study_key, "queries", annotation_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Query {annotation_id} not found in study {study_key}")
        return Query.from_json(raw[0])
