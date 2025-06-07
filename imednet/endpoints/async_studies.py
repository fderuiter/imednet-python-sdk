"""Async endpoint for managing studies."""

from typing import Any, List, Optional, cast

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.studies import Study


class AsyncStudiesEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with studies."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Study]:
        paginator = cast(
            AsyncPaginator,
            build_paginator(
                self,
                AsyncPaginator,
                "",
                None,
                page_size,
                filters,
                require_study=False,
            ),
        )
        return [Study.model_validate(item) async for item in paginator]

    async def get(self, study_key: str) -> Study:
        path = self._build_path(study_key)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Study {study_key} not found")
        return Study.model_validate(raw[0])
