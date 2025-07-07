"""Endpoint for managing queries (dialogue/questions) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.queries import Query


class QueriesEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with queries (dialogue/questions) in an iMedNet study.

    Provides methods to list and retrieve queries.
    """

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Query]:  # type: ignore[override]
        """List queries in a study with optional filtering."""
        result = self._list_common(False, study_key=study_key, **filters)
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Query]:  # type: ignore[override]
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(True, study_key=study_key, **filters)
        return result

    def get(self, study_key: str, annotation_id: int) -> Query:  # type: ignore[override]
        """
        Get a specific query by annotation ID.

        The annotation ID filter is forwarded to :meth:`list`.

        Args:
            study_key: Study identifier
            annotation_id: Query annotation identifier

        Returns:
            Query object
        """
        result = self._get_common(False, study_key=study_key, item_id=annotation_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, annotation_id: int) -> Query:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        This call filters :meth:`async_list` by ``annotation_id``.
        """
        return await self._get_common(True, study_key=study_key, item_id=annotation_id)
