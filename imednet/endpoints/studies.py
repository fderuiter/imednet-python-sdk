"""Endpoint for managing studies in the iMedNet system."""

from typing import Any, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints._mixins import ListGetEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.studies import Study


class StudiesEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    _cache_name = "_studies_cache"
    requires_study_key = False
    _studies_cache: Optional[List[Study]]

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._studies_cache: Optional[List[Study]] = None

    def list(self, refresh: bool = False, **filters) -> List[Study]:
        """List studies with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, refresh: bool = False, **filters: Any) -> List[Study]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            refresh=refresh,
            **filters,
        )
        return result

    def get(self, study_key: str) -> Study:
        """
        Get a specific study by key.

        This endpoint maintains a local cache. ``refresh=True`` is passed to
        :meth:`list` to ensure the latest data is fetched for the lookup.

        Args:
            study_key: Study identifier

        Returns:
            Study object
        """
        result = self._get_impl(self._client, Paginator, study_key=None, item_id=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str) -> Study:
        """Asynchronous version of :meth:`get`.

        Like the synchronous variant, this call passes ``refresh=True`` to
        :meth:`async_list` to bypass the cache.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, study_key=None, item_id=study_key
        )
