"""Endpoint for managing sites (study locations) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.sites import Site
from imednet.utils.filters import build_filter_string


class SitesEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Site]:
        """
        List sites in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Site objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "sites")
        paginator = Paginator(self._client, path, params=params)
        return [Site.from_json(item) for item in paginator]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Site]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "sites")
        paginator = AsyncPaginator(self._async_client, path, params=params)
        return [Site.from_json(item) async for item in paginator]

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
        sites = self.list(study_key=study_key, siteId=site_id)
        if not sites:
            raise ValueError(f"Site {site_id} not found in study {study_key}")
        return sites[0]

    async def async_get(self, study_key: str, site_id: int) -> Site:
        """Asynchronous version of :meth:`get`.

        This method also filters :meth:`async_list` by ``site_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        sites = await self.async_list(study_key=study_key, siteId=site_id)
        if not sites:
            raise ValueError(f"Site {site_id} not found in study {study_key}")
        return sites[0]
