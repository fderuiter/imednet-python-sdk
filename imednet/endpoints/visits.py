"""Endpoint for managing visits (interval instances) in a study."""

import inspect
from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.visits import Visit
from imednet.utils.filters import build_filter_string


class VisitsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
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

        path = self._build_path(filters.get("studyKey", ""), "visits")
        paginator = paginator_cls(client, path, params=params)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Visit]:
                return [Visit.from_json(item) async for item in paginator]

            return _collect()

        return [Visit.from_json(item) for item in paginator]

    def _get_impl(
        self, client: Any, paginator_cls: type[Any], study_key: str, visit_id: int
    ) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            visitId=visit_id,
        )

        if inspect.isawaitable(result):

            async def _await() -> Visit:
                items = await result
                if not items:
                    raise ValueError(f"Visit {visit_id} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Visit {visit_id} not found in study {study_key}")
        return result[0]

    def list(self, study_key: Optional[str] = None, **filters) -> List[Visit]:
        """List visits in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Visit]:
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

    def get(self, study_key: str, visit_id: int) -> Visit:
        """
        Get a specific visit by ID.

        ``visit_id`` is sent as a filter to :meth:`list` for retrieval.

        Args:
            study_key: Study identifier
            visit_id: Visit identifier

        Returns:
            Visit object
        """
        result = self._get_impl(self._client, Paginator, study_key, visit_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, visit_id: int) -> Visit:
        """Asynchronous version of :meth:`get`.

        The asynchronous call also filters by ``visit_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key, visit_id)
