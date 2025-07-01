"""Endpoint for managing sites (study locations) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.sites import Site


class SitesEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with sites in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Site
    PATH_SUFFIX = "sites"
    ID_FILTER = "siteId"

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Site]:
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
        """Get a specific site by ID."""
        result = self._get_impl(self._client, Paginator, site_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, site_id: int) -> Site:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, site_id, study_key=study_key
        )
