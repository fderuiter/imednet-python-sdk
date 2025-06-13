"""Endpoint for managing queries (dialogue/questions) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.queries import Query
from imednet.utils.filters import build_filter_string


class QueriesEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with queries (dialogue/questions) in an iMedNet study.

    Provides methods to list and retrieve queries.
    """

    PATH = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Query]:
        """
        List queries in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Query objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "queries")
        paginator = Paginator(self._client, path, params=params)
        return [Query.from_json(item) for item in paginator]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Query]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "queries")
        paginator = AsyncPaginator(self._async_client, path, params=params)
        return [Query.from_json(item) async for item in paginator]

    def get(self, study_key: str, annotation_id: int) -> Query:
        """
        Get a specific query by annotation ID.

        Args:
            study_key: Study identifier
            annotation_id: Query annotation identifier

        Returns:
            Query object
        """
        path = self._build_path(study_key, "queries", annotation_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Query {annotation_id} not found in study {study_key}")
        return Query.from_json(raw[0])

    async def async_get(self, study_key: str, annotation_id: int) -> Query:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        path = self._build_path(study_key, "queries", annotation_id)
        raw = (await self._async_client.get(path)).json().get("data", [])
        if not raw:
            raise ValueError(f"Query {annotation_id} not found in study {study_key}")
        return Query.from_json(raw[0])
