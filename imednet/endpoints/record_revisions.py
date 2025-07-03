"""Endpoint for retrieving record revision history in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.record_revisions import RecordRevision
from imednet.utils.filters import build_filter_string as _build_filter_string

from ._mixins import ListGetEndpointMixin

# expose for patching in tests
build_filter_string = _build_filter_string


class RecordRevisionsEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "recordRevisions"
    MODEL = RecordRevision
    ID_FIELD = "recordRevisionId"
    _include_study_key_in_filter = True

    def list(self, study_key: Optional[str] = None, **filters) -> List[RecordRevision]:
        """List record revisions in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(
        self, study_key: Optional[str] = None, **filters: Any
    ) -> List[RecordRevision]:
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

    def get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """
        Get a specific record revision by ID.

        The ID is forwarded to :meth:`list` as a filter; no caching is used.

        Args:
            study_key: Study identifier
            record_revision_id: Record revision identifier

        Returns:
            RecordRevision object
        """
        result = self._get_impl(
            self._client,
            Paginator,
            study_key=study_key,
            item_id=record_revision_id,
        )
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """Asynchronous version of :meth:`get`.

        This call also filters :meth:`async_list` by ``record_revision_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            item_id=record_revision_id,
        )
