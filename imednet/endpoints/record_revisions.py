"""Endpoint for retrieving record revision history in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsEndpoint(PagedEndpointMixin):
    """API endpoint for accessing record revision history in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = RecordRevision
    PATH_SUFFIX = "recordRevisions"
    ID_FILTER = "recordRevisionId"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[RecordRevision]:
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
        """Get a specific record revision by ID."""
        result = self._get_impl(self._client, Paginator, record_revision_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            record_revision_id,
            study_key=study_key,
        )
