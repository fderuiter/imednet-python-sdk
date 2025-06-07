"""Async endpoint for managing records (eCRF instances) in a study."""

from typing import Any, Dict, List, Optional, Union, cast

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.utils.filters import build_filter_string


class AsyncRecordsEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with records."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        study_key: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Record]:
        extra: Dict[str, Any] = {}
        if isinstance(record_data_filter, (dict, list)):
            extra["recordDataFilter"] = build_filter_string(
                record_data_filter, and_connector=";", or_connector=","
            )
        elif record_data_filter:
            extra["recordDataFilter"] = record_data_filter

        paginator = cast(
            AsyncPaginator,
            build_paginator(
                self,
                AsyncPaginator,
                "records",
                study_key,
                page_size,
                filters,
                extra_params=extra,
            ),
        )
        return [Record.from_json(item) async for item in paginator]

    async def get(self, study_key: str, record_id: Union[str, int]) -> Record:
        path = self._build_path(study_key, "records", record_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"Record {record_id} not found in study {study_key}")
        return Record.from_json(raw[0])

    async def create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
    ) -> Job:
        path = self._build_path(study_key, "records")
        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                headers["x-email-notify"] = email_notify
            else:
                headers["x-email-notify"] = str(email_notify).lower()

        response = await self._client.post(path, json=records_data, headers=headers)
        return Job.from_json(response.json())
