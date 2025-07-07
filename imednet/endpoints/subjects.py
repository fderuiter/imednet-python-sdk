"""Endpoint for managing subjects in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.subjects import Subject


class SubjectsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Subject]:  # type: ignore[override]
        """List subjects in a study with optional filtering."""
        result = self._list_common(False, study_key=study_key, **filters)
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Subject]:  # type: ignore[override]
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(True, study_key=study_key, **filters)
        return result

    def get(self, study_key: str, subject_key: str) -> Subject:  # type: ignore[override]
        """
        Get a specific subject by key.

        The ``subject_key`` is passed as a filter to :meth:`list`.

        Args:
            study_key: Study identifier
            subject_key: Subject identifier

        Returns:
            Subject object
        """
        result = self._get_common(False, study_key=study_key, item_id=subject_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, subject_key: str) -> Subject:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        This call also filters :meth:`async_list` by ``subject_key``.
        """
        return await self._get_common(True, study_key=study_key, item_id=subject_key)
