"""Endpoint for managing intervals (visit definitions) in a study."""

from typing import Any, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.intervals import Interval


class IntervalsEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with intervals in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Interval
    PATH_SUFFIX = "intervals"
    ID_FILTER = "intervalId"
    PAGE_SIZE = 500
    CACHE_ENABLED = True

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)

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
        """Get a specific interval by ID."""
        result = self._get_impl(self._client, Paginator, interval_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, interval_id: int) -> Interval:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, interval_id, study_key=study_key
        )
