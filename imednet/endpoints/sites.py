"""Endpoint for managing sites (study locations) in a study."""

import inspect
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

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        **filters: Any,
    ) -> Any:
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
        paginator = paginator_cls(client, path, params=params)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Site]:
                return [Site.from_json(item) async for item in paginator]

            return _collect()

        return [Site.from_json(item) for item in paginator]

    def _get_impl(self, client: Any, paginator_cls: type[Any], study_key: str, site_id: int) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            siteId=site_id,
        )

        if inspect.isawaitable(result):

            async def _await() -> Site:
                items = await result
                if not items:
                    raise ValueError(f"Site {site_id} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Site {site_id} not found in study {study_key}")
        return result[0]

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
        result = self._get_impl(self._client, Paginator, study_key, site_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, site_id: int) -> Site:
        """Asynchronous version of :meth:`get`.

        This method also filters :meth:`async_list` by ``site_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key, site_id)
