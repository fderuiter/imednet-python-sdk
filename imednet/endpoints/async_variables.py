"""Async endpoint for managing variables in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.variables import Variable
from imednet.utils.filters import build_filter_string


class AsyncVariablesEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with variables."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx) -> None:
        super().__init__(client, ctx)

    async def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Variable]:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "variables")
        paginator = AsyncPaginator(self._client, path, params=params, page_size=500)
        return [Variable.from_json(item) async for item in paginator]

    async def get(self, study_key: str, variable_id: int) -> Variable:
        path = self._build_path(study_key, "variables", variable_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Variable {variable_id} not found in study {study_key}")
        return Variable.from_json(raw[0])
