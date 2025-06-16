"""Endpoint for managing intervals (visit definitions) in a study."""

import inspect
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

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> Any:
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
        paginator = paginator_cls(client, path, params=params, page_size=500)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Interval]:
                result = [Interval.from_json(item) async for item in paginator]
                if not filters:
                    self._intervals_cache[study] = result
                return result

            return _collect()

        result = [Interval.from_json(item) for item in paginator]
        if not filters:
            self._intervals_cache[study] = result
        return result

    def _get_impl(
        self, client: Any, paginator_cls: type[Any], study_key: str, interval_id: int
    ) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            intervalId=interval_id,
        )

        if inspect.isawaitable(result):

            async def _await() -> Interval:
                items = await result
                if not items:
                    raise ValueError(f"Interval {interval_id} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Interval {interval_id} not found in study {study_key}")
        return result[0]

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
        """List intervals in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Interval]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result

    def get(self, study_key: str, interval_id: int) -> Interval:
        """
        Get a specific interval by ID.

        ``refresh=True`` is passed to :meth:`list` to override the cached
        interval list when performing the lookup.

        Args:
            study_key: Study identifier
            interval_id: Interval identifier

        Returns:
            Interval object
        """
        result = self._get_impl(self._client, Paginator, study_key, interval_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, interval_id: int) -> Interval:
        """Asynchronous version of :meth:`get`.

        The asynchronous call also passes ``refresh=True`` to
        :meth:`async_list`.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key, interval_id)
