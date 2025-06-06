"""Async endpoint for managing studies."""

from typing import Any, Dict, List

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.studies import Study
from imednet.utils.filters import build_filter_string


class AsyncStudiesEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with studies."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx) -> None:
        super().__init__(client, ctx)

    async def list(self, **filters: Any) -> List[Study]:
        filters = self._auto_filter(filters)
        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        paginator = AsyncPaginator(self._client, self.path, params=params)
        return [Study.model_validate(item) async for item in paginator]

    async def get(self, study_key: str) -> Study:
        path = self._build_path(study_key)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Study {study_key} not found")
        return Study.model_validate(raw[0])
