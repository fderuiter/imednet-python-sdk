"""Endpoint for managing visits (interval instances) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.visits import Visit


class VisitsEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with visits in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Visit
    PATH_SUFFIX = "visits"
    ID_FILTER = "visitId"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Visit]:
        """List visits in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Visit]:
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

    def get(self, study_key: str, visit_id: int) -> Visit:
        """Get a specific visit by ID."""
        result = self._get_impl(self._client, Paginator, visit_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, visit_id: int) -> Visit:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, visit_id, study_key=study_key
        )
