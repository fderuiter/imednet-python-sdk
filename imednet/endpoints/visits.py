"""Endpoint for managing visits (interval instances) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.visits import Visit


class VisitsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
    """

    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Visit]:  # type: ignore[override]
        """List visits in a study with optional filtering."""
        result = self._list_common(False, study_key=study_key, **filters)
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Visit]:  # type: ignore[override]
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(True, study_key=study_key, **filters)
        return result

    def get(self, study_key: str, visit_id: int) -> Visit:  # type: ignore[override]
        """
        Get a specific visit by ID.

        ``visit_id`` is sent as a filter to :meth:`list` for retrieval.

        Args:
            study_key: Study identifier
            visit_id: Visit identifier

        Returns:
            Visit object
        """
        result = self._get_common(False, study_key=study_key, item_id=visit_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, visit_id: int) -> Visit:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        The asynchronous call also filters by ``visit_id``.
        """
        return await self._get_common(True, study_key=study_key, item_id=visit_id)
