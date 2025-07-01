"""Endpoint for managing queries (dialogue/questions) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.queries import Query


class QueriesEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with queries in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Query
    PATH_SUFFIX = "queries"
    ID_FILTER = "annotationId"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Query]:
        """List queries in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Query]:
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

    def get(self, study_key: str, annotation_id: int) -> Query:
        """Get a specific query by annotation ID."""
        result = self._get_impl(self._client, Paginator, annotation_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, annotation_id: int) -> Query:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, annotation_id, study_key=study_key
        )
