"""Endpoint for retrieving record revision history in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsEndpoint(ListGetEndpoint):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"

    def list(self, study_key: Optional[str] = None, **filters) -> List[RecordRevision]:  # type: ignore[override]
        """List record revisions in a study with optional filtering."""
        result = self._list_common(False, study_key=study_key, **filters)
        return result  # type: ignore[return-value]

    async def async_list(  # type: ignore[override]
        self, study_key: Optional[str] = None, **filters: Any
    ) -> List[RecordRevision]:
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(True, study_key=study_key, **filters)
        return result

    def get(self, study_key: str, record_revision_id: int) -> RecordRevision:  # type: ignore[override]
        """
        Get a specific record revision by ID.

        The ID is forwarded to :meth:`list` as a filter; no caching is used.

        Args:
            study_key: Study identifier
            record_revision_id: Record revision identifier

        Returns:
            RecordRevision object
        """
        result = self._get_common(False, study_key=study_key, item_id=record_revision_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, record_revision_id: int) -> RecordRevision:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        This call also filters :meth:`async_list` by ``record_revision_id``.
        """
        return await self._get_common(True, study_key=study_key, item_id=record_revision_id)
