"""Endpoint for managing studies in the iMedNet system."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.studies import Study
from imednet.utils.filters import build_filter_string


class StudiesEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    PATH = "/api/v1/edc/studies"

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._studies_cache: Optional[List[Study]] = None

    def list(self, refresh: bool = False, **filters) -> List[Study]:
        """
        List studies with optional filtering.

        Args:
            **filters: Filter parameters

        Returns:
            List of Study objects
        """
        filters = self._auto_filter(filters)
        if not filters and not refresh and self._studies_cache is not None:
            return self._studies_cache

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        paginator = Paginator(self._client, self.PATH, params=params)
        result = [Study.model_validate(item) for item in paginator]
        if not filters:
            self._studies_cache = result
        return result

    async def async_list(self, refresh: bool = False, **filters: Any) -> List[Study]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if not filters and not refresh and self._studies_cache is not None:
            return self._studies_cache

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        paginator = AsyncPaginator(self._async_client, self.PATH, params=params)
        result = [Study.model_validate(item) async for item in paginator]
        if not filters:
            self._studies_cache = result
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
        studies = self.list(refresh=True, studyKey=study_key)
        if not studies:
            raise ValueError(f"Study {study_key} not found")
        return studies[0]

    async def async_get(self, study_key: str) -> Study:
        """Asynchronous version of :meth:`get`.

        Like the synchronous variant, this call passes ``refresh=True`` to
        :meth:`async_list` to bypass the cache.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        studies = await self.async_list(refresh=True, studyKey=study_key)
        if not studies:
            raise ValueError(f"Study {study_key} not found")
        return studies[0]
