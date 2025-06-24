"""Endpoint for retrieving record revision history in a study."""

import inspect
from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.record_revisions import RecordRevision
from imednet.utils.filters import build_filter_string


class RecordRevisionsEndpoint(BaseEndpoint):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "/api/v1/edc/studies"

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        **filters: Any,
    ) -> Any:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "recordRevisions")
        paginator = paginator_cls(client, path, params=params)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[RecordRevision]:
                return [RecordRevision.from_json(item) async for item in paginator]

            return _collect()

        return [RecordRevision.from_json(item) for item in paginator]

    def _get_impl(
        self, client: Any, paginator_cls: type[Any], study_key: str, record_revision_id: int
    ) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            recordRevisionId=record_revision_id,
        )

        if inspect.isawaitable(result):

            async def _await() -> RecordRevision:
                items = await result
                if not items:
                    raise ValueError(
                        f"Record revision {record_revision_id} not found in study {study_key}"
                    )
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Record revision {record_revision_id} not found in study {study_key}")
        return result[0]

    def list(self, study_key: Optional[str] = None, **filters) -> List[RecordRevision]:
        """List record revisions in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(
        self, study_key: Optional[str] = None, **filters: Any
    ) -> List[RecordRevision]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            **filters,
        )
        return result

    def get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """
        Get a specific record revision by ID.

        The ID is forwarded to :meth:`list` as a filter; no caching is used.

        Args:
            study_key: Study identifier
            record_revision_id: Record revision identifier

        Returns:
            RecordRevision object
        """
        result = self._get_impl(self._client, Paginator, study_key, record_revision_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """Asynchronous version of :meth:`get`.

        This call also filters :meth:`async_list` by ``record_revision_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, study_key, record_revision_id
        )
