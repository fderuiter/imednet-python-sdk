"""Async endpoint for managing intervals in a study."""

from typing import Any, List, Optional, cast

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.intervals import Interval


class AsyncIntervalsEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with intervals."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Interval]:
        paginator = cast(
            AsyncPaginator,
            build_paginator(
                self,
                AsyncPaginator,
                "intervals",
                study_key,
                page_size,
                filters,
            ),
        )
        return [Interval.from_json(item) async for item in paginator]

    async def get(self, study_key: str, interval_id: int) -> Interval:
        path = self._build_path(study_key, "intervals", interval_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Interval {interval_id} not found in study {study_key}")
        return Interval.from_json(raw[0])
