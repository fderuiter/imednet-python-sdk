"""Endpoint for managing sites (study locations) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.sites import Site


class SitesEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    _pop_study_filter = True
    _missing_study_exception = KeyError

    def list(self, study_key: Optional[str] = None, **filters) -> List[Site]:  # type: ignore[override]
        """List sites in a study with optional filtering."""
        result = self._list_common(False, study_key=study_key, **filters)
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Site]:  # type: ignore[override]
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(True, study_key=study_key, **filters)
        return result

    def get(self, study_key: str, site_id: int) -> Site:  # type: ignore[override]
        """
        Get a specific site by ID.

        The ``site_id`` is applied as a filter when calling :meth:`list`.

        Args:
            study_key: Study identifier
            site_id: Site identifier

        Returns:
            Site object
        """
        result = self._get_common(False, study_key=study_key, item_id=site_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, site_id: int) -> Site:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        This method also filters :meth:`async_list` by ``site_id``.
        """
        return await self._get_common(True, study_key=study_key, item_id=site_id)
