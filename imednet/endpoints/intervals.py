"""Endpoint for managing intervals (visit definitions) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.intervals import Interval


class IntervalsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    PATH = "intervals"
    MODEL = Interval
    _id_param = "intervalId"
    _cache_name = "_intervals_cache"
    PAGE_SIZE = 500
    _pop_study_filter = True

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._intervals_cache: Dict[str, List[Interval]] = {}

    def list(  # type: ignore[override]
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Interval]:
        """List intervals in a study with optional filtering."""
        result = self._list_common(
            False,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(  # type: ignore[override]
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Interval]:
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(
            True,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result

    def get(self, study_key: str, interval_id: int) -> Interval:  # type: ignore[override]
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
        result = self._get_common(False, study_key=study_key, item_id=interval_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, interval_id: int) -> Interval:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        The asynchronous call also passes ``refresh=True`` to
        :meth:`async_list`.
        """
        return await self._get_common(True, study_key=study_key, item_id=interval_id)
