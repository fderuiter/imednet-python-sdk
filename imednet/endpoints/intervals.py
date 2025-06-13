"""Endpoint for managing intervals (visit definitions) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.intervals import Interval
from imednet.utils.filters import build_filter_string


class IntervalsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    PATH = "/api/v1/edc/studies"

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._intervals_cache: Dict[str, List[Interval]] = {}

    def list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Interval]:
        """
        List intervals in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Interval objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")
        if not filters and not refresh and study in self._intervals_cache:
            return self._intervals_cache[study]

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "intervals")
        paginator = Paginator(self._client, path, params=params, page_size=500)
        result = [Interval.from_json(item) for item in paginator]
        if not filters:
            self._intervals_cache[study] = result
        return result

    async def async_list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Interval]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")
        if not filters and not refresh and study in self._intervals_cache:
            return self._intervals_cache[study]

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "intervals")
        paginator = AsyncPaginator(self._async_client, path, params=params, page_size=500)
        result = [Interval.from_json(item) async for item in paginator]
        if not filters:
            self._intervals_cache[study] = result
        return result

    def get(self, study_key: str, interval_id: int) -> Interval:
        """
        Get a specific interval by ID.

        Args:
            study_key: Study identifier
            interval_id: Interval identifier

        Returns:
            Interval object
        """
        path = self._build_path(study_key, "intervals", interval_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Interval {interval_id} not found in study {study_key}")
        return Interval.from_json(raw[0])

    async def async_get(self, study_key: str, interval_id: int) -> Interval:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        path = self._build_path(study_key, "intervals", interval_id)
        raw = (await self._async_client.get(path)).json().get("data", [])
        if not raw:
            raise ValueError(f"Interval {interval_id} not found in study {study_key}")
        return Interval.from_json(raw[0])
