"""Async endpoint for retrieving record revision history in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.record_revisions import RecordRevision
from imednet.utils.filters import build_filter_string


class AsyncRecordRevisionsEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for accessing record revision history."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[RecordRevision]:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "recordRevisions")
        paginator = AsyncPaginator(
            self._client,
            path,
            params=params,
            page_size=page_size or self._default_page_size,
        )
        return [RecordRevision.from_json(item) async for item in paginator]

    async def get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        path = self._build_path(study_key, "recordRevisions", record_revision_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Record revision {record_revision_id} not found in study {study_key}")
        return RecordRevision.from_json(raw[0])
