"""Endpoint for managing codings (medical coding) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints._mixins import ListGetEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.codings import Coding


class CodingsEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
    _pop_study_filter = True
    _missing_study_exception = KeyError

    def list(self, study_key: Optional[str] = None, **filters) -> List[Coding]:
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
        """
        Get a specific coding by ID.

        The ``coding_id`` value is supplied as a filter to :meth:`list`.

        Args:
            study_key: Study identifier
            coding_id: Coding identifier

        Returns:
            Coding object
        """

        result = self._get_impl(self._client, Paginator, study_key=study_key, item_id=coding_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, coding_id: str) -> Coding:
        """Asynchronous version of :meth:`get`.

        This method also filters :meth:`async_list` by ``coding_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, study_key=study_key, item_id=coding_id
        )
