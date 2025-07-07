"""Endpoint for managing sites (study locations) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints._mixins import ListGetEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.sites import Site


class SitesEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    _pop_study_filter = True
    _missing_study_exception = KeyError

    def list(self, study_key: Optional[str] = None, **filters) -> List[Site]:
        """List sites in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Site]:
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

    def get(self, study_key: str, site_id: int) -> Site:
        """
        Get a specific site by ID.

        The ``site_id`` is applied as a filter when calling :meth:`list`.

        Args:
            study_key: Study identifier
            site_id: Site identifier

        Returns:
            Site object
        """
        result = self._get_impl(self._client, Paginator, study_key=study_key, item_id=site_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, site_id: int) -> Site:
        """Asynchronous version of :meth:`get`.

        This method also filters :meth:`async_list` by ``site_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, study_key=study_key, item_id=site_id
        )
