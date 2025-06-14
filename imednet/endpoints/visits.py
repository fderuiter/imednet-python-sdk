"""Endpoint for managing visits (interval instances) in a study."""

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

    def list(self, study_key: Optional[str] = None, **filters) -> List[Visit]:
        """
        List visits in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Visit objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "visits")
        paginator = Paginator(self._client, path, params=params)
        return [Visit.from_json(item) for item in paginator]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Visit]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "visits")
        paginator = AsyncPaginator(self._async_client, path, params=params)
        return [Visit.from_json(item) async for item in paginator]

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
        visits = self.list(study_key=study_key, visitId=visit_id)
        if not visits:
            raise ValueError(f"Visit {visit_id} not found in study {study_key}")
        return visits[0]

    async def async_get(self, study_key: str, visit_id: int) -> Visit:
        """Asynchronous version of :meth:`get`.

        The asynchronous call also filters by ``visit_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        visits = await self.async_list(study_key=study_key, visitId=visit_id)
        if not visits:
            raise ValueError(f"Visit {visit_id} not found in study {study_key}")
        return visits[0]
