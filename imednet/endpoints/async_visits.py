"""Async endpoint for managing visits in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.visits import Visit
from imednet.utils.filters import build_filter_string


class AsyncVisitsEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with visits."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx) -> None:
        super().__init__(client, ctx)

    async def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Visit]:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "visits")
        paginator = AsyncPaginator(self._client, path, params=params)
        return [Visit.from_json(item) async for item in paginator]

    async def get(self, study_key: str, visit_id: int) -> Visit:
        path = self._build_path(study_key, "visits", visit_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Visit {visit_id} not found in study {study_key}")
        return Visit.from_json(raw[0])
