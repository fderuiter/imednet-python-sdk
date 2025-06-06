"""Async endpoint for managing sites in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.sites import Site
from imednet.utils.filters import build_filter_string


class AsyncSitesEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with study sites."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Site]:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "sites")
        paginator = AsyncPaginator(
            self._client,
            path,
            params=params,
            page_size=page_size or self._default_page_size,
        )
        return [Site.from_json(item) async for item in paginator]

    async def get(self, study_key: str, site_id: int) -> Site:
        path = self._build_path(study_key, "sites", site_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Site {site_id} not found in study {study_key}")
        return Site.from_json(raw[0])
