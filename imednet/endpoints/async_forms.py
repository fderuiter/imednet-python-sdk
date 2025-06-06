"""Async endpoint for managing forms (eCRFs) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.forms import Form
from imednet.utils.filters import build_filter_string


class AsyncFormsEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with forms (eCRFs)."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx) -> None:
        super().__init__(client, ctx)

    async def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Form]:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "forms")
        paginator = AsyncPaginator(self._client, path, params=params, page_size=500)
        return [Form.from_json(item) async for item in paginator]

    async def get(self, study_key: str, form_id: int) -> Form:
        path = self._build_path(study_key, "forms", form_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Form {form_id} not found in study {study_key}")
        return Form.from_json(raw[0])
