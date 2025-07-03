"""Endpoint for managing visits (interval instances) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.visits import Visit
from imednet.utils.filters import build_filter_string as _build_filter_string

from ._mixins import ListGetEndpointMixin

# expose for patching in tests
build_filter_string = _build_filter_string


class VisitsEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
    """

    PATH = "visits"
    MODEL = Visit
    ID_FIELD = "visitId"
    _include_study_key_in_filter = True

    def list(self, study_key: Optional[str] = None, **filters) -> List[Visit]:
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
        """
        Get a specific visit by ID.

        ``visit_id`` is sent as a filter to :meth:`list` for retrieval.

        Args:
            study_key: Study identifier
            visit_id: Visit identifier

        Returns:
            Visit object
        """
        result = self._get_impl(
            self._client,
            Paginator,
            study_key=study_key,
            item_id=visit_id,
        )
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, visit_id: int) -> Visit:
        """Asynchronous version of :meth:`get`.

        The asynchronous call also filters by ``visit_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            item_id=visit_id,
        )
