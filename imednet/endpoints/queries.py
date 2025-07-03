"""Endpoint for managing queries (dialogue/questions) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints._mixins import ListGetEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.queries import Query


class QueriesEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with queries (dialogue/questions) in an iMedNet study.

    Provides methods to list and retrieve queries.
    """

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Query]:
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
        """
        Get a specific query by annotation ID.

        The annotation ID filter is forwarded to :meth:`list`.

        Args:
            study_key: Study identifier
            annotation_id: Query annotation identifier

        Returns:
            Query object
        """
        result = self._get_impl(self._client, Paginator, study_key, annotation_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, annotation_id: int) -> Query:
        """Asynchronous version of :meth:`get`.

        This call filters :meth:`async_list` by ``annotation_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key, annotation_id)
