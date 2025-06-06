"""Async endpoint for managing codings in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.codings import Coding
from imednet.utils.filters import build_filter_string


class AsyncCodingsEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with codings."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Coding]:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "codings")
        paginator = AsyncPaginator(
            self._client,
            path,
            params=params,
            page_size=page_size or self._default_page_size,
        )
        return [Coding.from_json(item) async for item in paginator]

    async def get(self, study_key: str, coding_id: str) -> Coding:
        path = self._build_path(study_key, "codings", coding_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Coding {coding_id} not found in study {study_key}")
        return Coding.from_json(raw[0])
