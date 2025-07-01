"""Endpoint for managing codings (medical coding) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.codings import Coding


class CodingsEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with codings in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Coding
    PATH_SUFFIX = "codings"
    ID_FILTER = "codingId"

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Coding]:
        """List codings in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Coding]:
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

    def get(self, study_key: str, coding_id: str) -> Coding:
        """Get a specific coding by ID."""
        result = self._get_impl(self._client, Paginator, coding_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, coding_id: str) -> Coding:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, coding_id, study_key=study_key
        )
